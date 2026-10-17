const dialog = document.querySelector("#action-dialog");
const form = document.querySelector("#action-form");
const toast = document.querySelector("#toast");
const productName = document.querySelector("#product-name");
const quantityInput = document.querySelector("#product-quantity");
const expiryInput = document.querySelector("#product-expiry");
const supplierInput = document.querySelector("#product-supplier");
const codeInput = document.querySelector("#product-code");
const codeLabel = document.querySelector("#code-label");
const photoInput = document.querySelector("#photo-input");
const dialogTitle = document.querySelector("#dialog-title");
const dialogCopy = document.querySelector("#dialog-copy");
const dialogEyebrow = document.querySelector("#dialog-eyebrow");
const submitButton = document.querySelector("#submit-button");

const products = [
  { name: "Arroz extra", quantity: 8, expiry: "", supplier: "" },
  { name: "Leche evaporada", quantity: 12, expiry: "", supplier: "" },
  { name: "Plátano de seda", quantity: 6, expiry: "hoy", supplier: "" },
  { name: "Galletas de vainilla", quantity: 4, expiry: "3 días", supplier: "" }
];

let currentMode = "write";
let toastTimer;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 2800);
}

function setMode(mode) {
  currentMode = mode;
  form.dataset.action = "add";
  form.dataset.mode = mode;
  dialogEyebrow.textContent = "NUEVO PRODUCTO";
  dialogTitle.textContent = "Agrega mercadería";
  submitButton.textContent = "Guardar producto";
  quantityInput.value = "1";
  expiryInput.value = "";
  supplierInput.value = "";
  codeInput.value = "";
  codeInput.hidden = mode !== "scan";
  codeLabel.hidden = mode !== "scan";
  productName.placeholder = mode === "voice"
    ? "Ej. 2 kilos de manzana"
    : "Ej. Leche evaporada";
  dialogCopy.textContent = mode === "photo"
    ? "Adjunta una foto de la boleta o el producto y completa los datos."
    : mode === "voice"
      ? "Dicta el nombre y la cantidad, luego revisa los datos."
      : mode === "scan"
        ? "Escribe el código del producto y completa lo que falta."
        : "Anota lo básico, puedes completar el resto después.";
  dialog.showModal();
  productName.focus();

  if (mode === "photo") {
    photoInput.click();
  }
  if (mode === "voice") {
    startVoiceEntry();
  }
}

function startVoiceEntry() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast("Puedes escribir el producto en el campo de arriba.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "es-PE";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.onresult = (event) => {
    productName.value = event.results[0][0].transcript;
    showToast("Listo, revisa el nombre y la cantidad.");
  };
  recognition.onerror = () => showToast("No pudimos escuchar. Escribe el producto para continuar.");
  recognition.start();
}

function updateProductCount() {
  document.querySelector("#product-count").textContent = products.length + 20;
}

document.querySelectorAll(".method-card").forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

document.querySelector("#dialog-close").addEventListener("click", () => dialog.close());

photoInput.addEventListener("change", () => {
  if (photoInput.files.length) {
    showToast(`Foto lista: ${photoInput.files[0].name}. Completa los datos del producto.`);
  }
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const name = productName.value.trim();
  const quantity = Number(quantityInput.value);

  if (!name || !Number.isInteger(quantity) || quantity < 1) {
    showToast("Revisa el nombre y la cantidad del producto.");
    return;
  }

  if (form.dataset.action === "sale") {
    const product = products.find((item) => item.name.toLowerCase() === name.toLowerCase());
    if (!product || product.quantity < quantity) {
      showToast("No hay suficientes unidades de ese producto en tu inventario.");
      return;
    }
    product.quantity -= quantity;
    dialog.close();
    form.reset();
    showToast(`Venta registrada. Quedan ${product.quantity} unidades de ${product.name}.`);
    return;
  }

  products.push({
    name,
    quantity,
    expiry: expiryInput.value,
    supplier: supplierInput.value.trim()
  });
  updateProductCount();
  dialog.close();
  form.reset();
  showToast(`${name} se agregó a tu inventario.`);
});

function openSaleForm() {
  form.dataset.action = "sale";
  form.dataset.mode = "sale";
  dialogEyebrow.textContent = "REGISTRO DE VENTA";
  dialogTitle.textContent = "¿Qué vendiste?";
  dialogCopy.textContent = "Anota el producto y la cantidad para actualizar tu stock.";
  submitButton.textContent = "Registrar venta";
  codeInput.hidden = true;
  codeLabel.hidden = true;
  productName.placeholder = "Ej. Arroz extra";
  quantityInput.value = "1";
  expiryInput.closest(".field-row").hidden = true;
  supplierInput.closest(".field-label").hidden = true;
  supplierInput.hidden = true;
  dialog.showModal();
  productName.focus();
}

function resetFormVisibility() {
  expiryInput.closest(".field-row").hidden = false;
  supplierInput.closest(".field-label").hidden = false;
  supplierInput.hidden = false;
  codeInput.hidden = currentMode !== "scan";
  codeLabel.hidden = currentMode !== "scan";
}

dialog.addEventListener("close", resetFormVisibility);
document.querySelector("#sale-button").addEventListener("click", openSaleForm);
document.querySelector("#sales-nav").addEventListener("click", openSaleForm);
document.querySelector("#supplier-tip").addEventListener("click", () => {
  showToast("Anota el proveedor al registrar el producto y solicita el cambio antes del vencimiento.");
});
document.querySelector("#inventory-nav").addEventListener("click", () => {
  showToast(`Tienes ${products.length + 20} productos registrados en tu inventario.`);
});
document.querySelector("#profile-nav").addEventListener("click", () => {
  showToast("Perfil de Rosa · Bodega Mi Rosita");
});
