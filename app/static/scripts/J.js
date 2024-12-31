// Toggle Menu for Small Screens
function toggleMenu() {
  const menu = document.getElementById('menu');
  menu.classList.toggle('show');  // Adds or removes the 'show' class
}

// Dropdown Toggle
const dropdown = document.querySelector('.dropdown');
const dropdownMenu = dropdown.querySelector('.dropdown-menu');

dropdown.addEventListener('click', () => {
  dropdownMenu.classList.toggle('show');  // Toggles visibility via class
});

// FullCalendar Initialization
document.addEventListener('DOMContentLoaded', () => {
  const calendarEl = document.getElementById('calendar');
  if (calendarEl) {
    const calendar = new Calendar(calendarEl, {
      plugins: [dayGridPlugin],
      initialView: 'dayGridMonth',
    });
    calendar.render();
  }
});

