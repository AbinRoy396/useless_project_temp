const API = window.CAMPUS_VOICE_API || (window.location.port === "8000" ? "http://127.0.0.1:8001" : window.location.origin);
const $ = (id) => document.getElementById(id);
let mood = 7;

const icons = {"Wi-Fi":"📶", Timetable:"🗓️", Attendance:"🧾", Infrastructure:"🪑", Canteen:"🍜", Transport:"🚌", Examination:"📝", Hostel:"🏠", Fees:"💳", Academic:"📚", Other:"📣"};
const escapeHtml = (value) => { const el = document.createElement("div"); el.textContent = value; return el.innerHTML; };

function renderDashboard(data) {
  $("score").textContent = data.campus_score.toFixed(1);
  $("level").textContent = data.level;
  $("meter").style.width = `${data.campus_score}%`;
  $("count").textContent = data.total_complaints;
  $("average").textContent = data.average_frustration.toFixed(1);
  $("source-count").textContent = `TODAY · ${data.total_complaints} REPORTS`;
  const maxCategory = Math.max(...data.categories.map((item) => item.count), 1);
  $("sources").innerHTML = data.categories.length ? data.categories.map((item) => `<div class="source"><div>${icons[item.name] || "📣"}</div><div><div class="source-name">${escapeHtml(item.name)}</div><div class="bar"><i style="width:${item.count / maxCategory * 100}%"></i></div></div><b>${item.count}</b></div>`).join("") : "<p class='eyebrow'>No reports yet today.</p>";
  $("recent").innerHTML = data.recent_complaints.length ? data.recent_complaints.map((item) => `<div class="item"><div class="avatar">${item.mood >= 8 ? "🤬" : item.mood >= 6 ? "😡" : "😕"}</div><p>${escapeHtml(item.message)}<time>${escapeHtml(item.anonymous_id)} · ${new Date(item.created_at + "Z").toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}</time></p><span class="tag">${escapeHtml(item.department)}</span></div>`).join("") : "<p class='eyebrow'>The stream is waiting for its first voice.</p>";
  const maxDepartment = Math.max(...data.departments.map((item) => item.count), 1);
  $("departments").innerHTML = data.departments.length ? data.departments.map((item) => `<div class="dept-row"><div>${escapeHtml(item.name)}<span>${item.count} reports</span></div><div class="bar"><i style="width:${item.count / maxDepartment * 100}%"></i></div></div>`).join("") : "<p class='eyebrow'>No department data yet.</p>";
}

async function request(path, options) {
  const response = await fetch(`${API}${path}`, options);
  if (!response.ok) throw new Error("The Campus Voice API is unavailable.");
  return response.json();
}

async function refreshDashboard() {
  try { renderDashboard(await request("/api/dashboard")); $("connection").innerHTML = '<i class="dot"></i> LIVE API'; }
  catch { $("connection").textContent = "API OFFLINE · START BACKEND"; }
}

async function showReport() {
  requireAdmin(async (token) => {
    try {
    const report = await request("/api/admin/reports/daily", {headers:{Authorization:`Bearer ${token}`}});
    $("report-count").textContent = report.total_complaints;
    $("report-score").textContent = report.campus_score.toFixed(1);
    $("report-top").textContent = report.top_concern;
    $("report-summary").textContent = report.executive_summary;
    $("report-roast").textContent = report.roast;
    $("roast").textContent = `“${report.roast}”`;
    $("report-actions").innerHTML = report.suggested_actions.map((action) => `<li>${escapeHtml(action)}</li>`).join("");
    $("report-modal").classList.add("open");
    } catch { alert("The admin report could not be loaded."); }
  });
}

document.querySelectorAll(".mood").forEach((button) => button.addEventListener("click", () => { document.querySelectorAll(".mood").forEach((item) => item.classList.remove("selected")); button.classList.add("selected"); mood = Number(button.dataset.mood); }));
$("complaint-form").addEventListener("submit", async (event) => {
  event.preventDefault(); const button = $("submit"); button.disabled = true; button.textContent = "ANALYZING…";
  try {
    const complaint = await request("/api/complaints", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({message:$("message").value.trim(), department:$("department").value, mood})});
    $("message").value = ""; button.textContent = `RECORDED · ${complaint.category.toUpperCase()} ✓`; await refreshDashboard(); setTimeout(() => button.textContent = "SUBMIT FRUSTRATION →", 1800);
  } catch (error) { alert(error.message); button.textContent = "SUBMIT FRUSTRATION →"; }
  finally { button.disabled = false; }
});
$("report-button").addEventListener("click", showReport); $("close-report").addEventListener("click", () => $("report-modal").classList.remove("open"));

let pendingAdminAction = null;

function updateAdminUi() {
  const signedIn = Boolean(sessionStorage.getItem("campus_voice_admin_token"));
  $("logout-button").style.display = signedIn ? "block" : "none";
  $("report-card").style.display = signedIn ? "block" : "none";
  document.querySelectorAll("[data-admin-only]").forEach((item) => item.style.display = signedIn ? "" : "none");
}

function requireAdmin(action) {
  const saved = sessionStorage.getItem("campus_voice_admin_token");
  if (saved) return action(saved);
  pendingAdminAction = action;
  $("admin-login-status").textContent = "";
  $("admin-modal").classList.add("open");
  $("admin-username").focus();
}

$("admin-login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const status = $("admin-login-status");
  status.textContent = "Signing in…";
  try {
    const login = await request("/api/admin/login", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({username:$("admin-username").value, password:$("admin-password").value})});
    sessionStorage.setItem("campus_voice_admin_token", login.access_token);
    $("admin-password").value = "";
    $("admin-modal").classList.remove("open");
    updateAdminUi();
    const action = pendingAdminAction; pendingAdminAction = null;
    if (action) action(login.access_token);
  } catch (error) { status.textContent = "Sign-in failed. Check your credentials and try again."; }
});
$("close-admin").addEventListener("click", () => { pendingAdminAction = null; $("admin-modal").classList.remove("open"); });

$("send-report").addEventListener("click", async () => {
  const button = $("send-report"), status = $("send-status"); status.textContent = "Admin approval required.";
  requireAdmin(async (token) => {
    try {
      button.disabled = true; status.textContent = "Recording approval…";
      const audit = await request("/api/admin/reports/daily/send", {method:"POST", headers:{"Content-Type":"application/json", Authorization:`Bearer ${token}`}, body:JSON.stringify({})});
      status.textContent = audit.status === "sent" ? `Sent and audited at ${new Date(audit.created_at + "Z").toLocaleTimeString()}.` : "Approval recorded in the audit log. Preview mode did not send email.";
    } catch (error) { sessionStorage.removeItem("campus_voice_admin_token"); updateAdminUi(); status.textContent = error.message; }
    finally { button.disabled = false; }
  });
});

async function showAudits() {
  requireAdmin(async (token) => {
    try {
    const audits = await request("/api/admin/report-audits", {headers:{Authorization:`Bearer ${token}`}});
    $("audit-list").innerHTML = audits.length ? audits.map((audit) => `<div class="item"><div class="avatar">${audit.status === "sent" ? "✓" : "◌"}</div><p><b>${escapeHtml(audit.status.toUpperCase())}</b> · ${escapeHtml(audit.recipient)}<time>${new Date(audit.created_at + "Z").toLocaleString()} · approved by ${escapeHtml(audit.approved_by)}</time></p><span class="tag">${escapeHtml(audit.subject)}</span></div>`).join("") : "<p class='eyebrow'>No report approvals recorded.</p>";
    $("audit-modal").classList.add("open");
    } catch (error) { $("audit-list").innerHTML = "<p class='eyebrow'>Unable to load the audit log.</p>"; }
  });
}
$("audit-button").addEventListener("click", showAudits);
$("close-audit").addEventListener("click", () => $("audit-modal").classList.remove("open"));
$("logout-button").addEventListener("click", () => { sessionStorage.removeItem("campus_voice_admin_token"); updateAdminUi(); });
updateAdminUi();

function connectWebSocket() {
  const wsUrl = API.replace(/^http/, "ws") + "/ws/dashboard";
  const socket = new WebSocket(wsUrl);
  socket.onopen = () => { $("connection").innerHTML = '<i class="dot"></i> LIVE WEBSOCKET'; socket.send("ready"); };
  socket.onmessage = () => refreshDashboard();
  socket.onclose = () => { $("connection").textContent = "RECONNECTING…"; setTimeout(connectWebSocket, 2500); };
  socket.onerror = () => socket.close();
}
refreshDashboard(); setInterval(refreshDashboard, 15000); connectWebSocket();

const pageLinks = {"Submit Frustration":"submit.html", "Campus Pulse":"pulse.html", "Daily Report":"email.html", "🔥 Roast":"roast.html"};
document.querySelectorAll(".nav a").forEach((link) => { if (pageLinks[link.textContent.trim()]) link.href = pageLinks[link.textContent.trim()]; });
