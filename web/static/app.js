const output = document.querySelector("#output");
const statusLine = document.querySelector("#statusLine");

function setStatus(text, kind = "idle") {
  statusLine.textContent = text;
  statusLine.className = `status ${kind}`;
}

function show(value) {
  if (typeof value === "string") {
    output.textContent = value;
  } else {
    output.textContent = JSON.stringify(value, null, 2);
  }
}

function appendFiles(form, field, input) {
  for (const file of input.files) {
    form.append(field, file, file.name);
  }
}

function appendCheckbox(form, field, input) {
  form.append(field, input.checked ? "true" : "false");
}

async function postForm(url, form) {
  setStatus("Running...", "running");
  const response = await fetch(url, { method: "POST", body: form });
  const data = await response.json();
  const ok = response.ok && data.exit_code === 0;
  setStatus(ok ? "Done" : `Exit ${data.exit_code ?? response.status}`, ok ? "ok" : "error");
  return data;
}

function renderRunResult(data) {
  const chunks = [];
  if (data.command && data.command.length) {
    chunks.push(`$ ${data.command.join(" ")}`);
  }
  if (data.stdout) {
    chunks.push(data.stdout.trimEnd());
  }
  if (data.stderr) {
    chunks.push(`stderr:\n${data.stderr.trimEnd()}`);
  }
  if (data.json) {
    chunks.push(JSON.stringify(data.json, null, 2));
  }
  show(chunks.filter(Boolean).join("\n\n"));
}

function downloadBase64(filename, base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  const blob = new Blob([bytes], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

document.querySelector("#runLint").addEventListener("click", async () => {
  const form = new FormData();
  appendFiles(form, "files", document.querySelector("#lintFiles"));
  form.append("record_text", document.querySelector("#recordText").value);
  form.append("server_paths", document.querySelector("#lintPaths").value);
  appendCheckbox(form, "strict", document.querySelector("#strict"));
  appendCheckbox(form, "strict_aging", document.querySelector("#strictAging"));
  appendCheckbox(form, "check_paths", document.querySelector("#checkPaths"));
  renderRunResult(await postForm("/api/lint", form));
});

document.querySelector("#runDag").addEventListener("click", async () => {
  const form = new FormData();
  appendFiles(form, "files", document.querySelector("#dagFiles"));
  form.append("server_paths", document.querySelector("#dagPaths").value);
  form.append("output_format", document.querySelector("#dagFormat").value);
  appendCheckbox(form, "use_examples", document.querySelector("#useExamples"));
  renderRunResult(await postForm("/api/dag", form));
});

document.querySelector("#runWorkbook").addEventListener("click", async () => {
  const form = new FormData();
  const workbook = document.querySelector("#workbookFile").files[0];
  if (workbook) {
    form.append("workbook", workbook, workbook.name);
  }
  form.append("server_path", document.querySelector("#workbookPath").value);
  form.append("net_columns", document.querySelector("#netColumns").value);
  form.append("pin_columns", document.querySelector("#pinColumns").value);
  form.append("skip_sheets", document.querySelector("#skipSheets").value);
  const data = await postForm("/api/format-pin-workbook", form);
  renderRunResult(data);
  if (data.exit_code === 0 && data.content_base64 && data.filename) {
    downloadBase64(data.filename, data.content_base64);
  }
});

document.querySelector("#runDoctor").addEventListener("click", async () => {
  const form = new FormData();
  renderRunResult(await postForm("/api/doctor", form));
});

document.querySelector("#clearOutput").addEventListener("click", () => {
  show("");
  setStatus("Idle");
});

fetch("/api/health")
  .then((response) => response.json())
  .then((data) => {
    document.querySelector("#repoRoot").textContent = data.repo_root;
  })
  .catch(() => {
    document.querySelector("#repoRoot").textContent = "Health check failed";
  });
