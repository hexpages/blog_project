// Mobile search toggle
document
  .getElementById("mobile-search-btn")
  .addEventListener("click", function () {
    const mobileSearch = document.getElementById("mobile-search");
    mobileSearch.classList.toggle("hidden");
  });

// Mobile menu toggle
document
  .getElementById("mobile-menu-btn")
  .addEventListener("click", function () {
    const mobileMenu = document.getElementById("mobile-menu");
    mobileMenu.classList.toggle("hidden");
  });

// Toggle profile dropdown
document.getElementById("profile-btn").addEventListener("click", function () {
  const dropdown = document.getElementById("profile-dropdown");
  dropdown.classList.toggle("hidden");
});

// Close dropdown when clicking outside
document.addEventListener("click", function (event) {
  const dropdown = document.getElementById("profile-dropdown");
  const profileBtn = document.getElementById("profile-btn");

  if (!profileBtn.contains(event.target)) {
    dropdown.classList.add("hidden");
  }
});
