document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector("button[type=submit]");
      if (btn) {
        btn.disabled = true;
        btn.style.opacity = ".85";
      }
    });
  });

  const product = document.querySelector("#product_id");
  const quantity = document.querySelector("#quantity");
  const addBtn = document.querySelector("#add-product");
  if (product && quantity && addBtn) {
    const validate = () => {
      const missingProduct = !product.value;
      const missingQuantity = !quantity.value || Number(quantity.value) <= 0;
      product.classList.toggle("invalid", missingProduct && document.activeElement !== product);
      quantity.classList.toggle("invalid", missingQuantity && document.activeElement !== quantity);
    };
    product.addEventListener("change", validate);
    quantity.addEventListener("input", validate);
  }
});
