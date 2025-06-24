// Camera and face authentication functionality
class CameraHandler {
  constructor() {
    this.stream = null;
    this.video = null;
    this.canvas = null;
    this.isActive = false;
  }

  async startCamera() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
      });

      this.video = document.getElementById("cameraFeed");
      this.canvas = document.getElementById("captureCanvas");

      this.video.srcObject = this.stream;
      this.isActive = true;

      return true;
    } catch (error) {
      console.error("Error accessing camera:", error);
      app.showNotification("Could not access camera", "error");
      return false;
    }
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }

    if (this.video) {
      this.video.srcObject = null;
    }

    this.isActive = false;
  }

  captureFrame() {
    if (!this.video || !this.canvas) return null;

    const context = this.canvas.getContext("2d");
    this.canvas.width = this.video.videoWidth;
    this.canvas.height = this.video.videoHeight;

    context.drawImage(this.video, 0, 0);

    return this.canvas.toDataURL("image/jpeg", 0.8);
  }
}

// Global camera handler
const cameraHandler = new CameraHandler();

// Face authentication functions
async function startFaceAuth() {
  const modal = document.getElementById("faceAuthModal");
  modal.classList.add("active");

  const started = await cameraHandler.startCamera();
  if (!started) {
    closeFaceAuth();
  }
}

function closeFaceAuth() {
  const modal = document.getElementById("faceAuthModal");
  modal.classList.remove("active");
  cameraHandler.stopCamera();

  // Hide register form
  document.getElementById("registerForm").style.display = "none";
}

async function authenticateWithFace() {
  if (!cameraHandler.isActive) {
    app.showNotification("Camera not active", "error");
    return;
  }

  const imageData = cameraHandler.captureFrame();
  if (!imageData) {
    app.showNotification("Could not capture image", "error");
    return;
  }

  try {
    const result = await eel.authenticate_with_face(imageData)();

    if (result.authenticated) {
      app.isAuthenticated = true;
      app.currentUser = result.user;
      app.updateUI();
      app.showNotification(`Welcome back, ${result.user}!`, "success");
      closeFaceAuth();
    } else {
      app.showNotification(result.message || "Authentication failed", "error");
    }
  } catch (error) {
    console.error("Authentication error:", error);
    app.showNotification("Authentication error occurred", "error");
  }
}

function showRegisterForm() {
  const registerForm = document.getElementById("registerForm");
  registerForm.style.display = "block";
  document.getElementById("userName").focus();
}

async function registerFace() {
  const userName = document.getElementById("userName").value.trim();

  if (!userName) {
    app.showNotification("Please enter your name", "error");
    return;
  }

  if (!cameraHandler.isActive) {
    app.showNotification("Camera not active", "error");
    return;
  }

  const imageData = cameraHandler.captureFrame();
  if (!imageData) {
    app.showNotification("Could not capture image", "error");
    return;
  }

  try {
    const result = await eel.register_face(imageData, userName)();

    if (result.success) {
      app.showNotification("Face registered successfully!", "success");
      document.getElementById("registerForm").style.display = "none";
      document.getElementById("userName").value = "";
    } else {
      app.showNotification(result.error || "Registration failed", "error");
    }
  } catch (error) {
    console.error("Registration error:", error);
    app.showNotification("Registration error occurred", "error");
  }
}

// Close modal when clicking outside
document.getElementById("faceAuthModal").addEventListener("click", (e) => {
  if (e.target.id === "faceAuthModal") {
    closeFaceAuth();
  }
});
