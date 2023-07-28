let selectedDate;

// Function to open the calendar popup
function openCalendarPopup() {
  const dateInput = document.createElement('input');
  dateInput.type = 'datetime-local'; // Use 'datetime-local' input type to select both date and time
  dateInput.addEventListener('change', () => {
    selectedDate = new Date(dateInput.value);
    alert('Date and time selected successfully!');
  });

  // Append the date input element to the document body
  document.body.appendChild(dateInput);
}

// Function to show the selected date and time
function showSelectedDate() {
  if (selectedDate) {
    document.getElementById('selectedDate').innerText = selectedDate.toLocaleString();
  } else {
    document.getElementById('selectedDate').innerText = 'No date and time selected.';
  }
}

// Add click event listeners to the buttons
document.getElementById('buttonA').addEventListener('click', openCalendarPopup);
document.getElementById('buttonB').addEventListener('click', showSelectedDate);
