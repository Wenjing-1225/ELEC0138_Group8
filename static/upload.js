document.addEventListener("DOMContentLoaded", function () {
    const uploadPanel = document.getElementById("upload-panel");
    const fileInput = document.getElementById("fileInput");

    if (uploadPanel) {
        uploadPanel.addEventListener("dragover", function (event) {
            event.preventDefault();
            uploadPanel.style.background = "linear-gradient(135deg, #f39c12, #e67e22)";
        });

        uploadPanel.addEventListener("dragleave", function () {
            uploadPanel.style.background = "linear-gradient(135deg, #f8e3a3, #f1c40f)";
        });

        uploadPanel.addEventListener("drop", function (event) {
            event.preventDefault();
            uploadPanel.style.background = "linear-gradient(135deg, #f8e3a3, #f1c40f)";
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                uploadFile(files[0]);
            }
        });

        uploadPanel.addEventListener("click", function () {
            fileInput.click();
        });

        fileInput.addEventListener("change", function () {
            if (fileInput.files.length > 0) {
                uploadFile(fileInput.files[0]);
            }
        });

        function uploadFile(file) {
            const formData = new FormData();
            formData.append("file", file);

            uploadPanel.innerHTML = "<p>Uploading...</p>";
            uploadPanel.style.opacity = "0.6";

            fetch("/upload", {
                method: "POST",
                body: formData
            })
            .then(response => response.text())
            .then(data => {
                uploadPanel.innerHTML = "<i class='fas fa-check-circle fa-2x text-success'></i><p>File uploaded!</p>";
                setTimeout(() => location.reload(), 1000);
            })
            .catch(error => {
                uploadPanel.innerHTML = "<p class='text-danger'>Upload failed.</p>";
            });
        }
    }
});
