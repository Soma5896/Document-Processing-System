async function uploadFile() {
  const input = document.getElementById("fileInput");
  const file = input.files[0];
  const status = document.getElementById("status");
  const result = document.getElementById("result");

  if (!file) {
    status.textContent = "❌ Please select a file.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  status.textContent = "⏳ Uploading and processing...";

  try {
    const response = await fetch("http://localhost:8000/process/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      status.textContent = `❌ Error: ${errorData.error}`;
      return;
    }

    const data = await response.json();
    status.textContent = "✅ Processing complete!";
    result.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    status.textContent = "❌ Failed to connect to backend.";
    result.textContent = "";
  }
}
