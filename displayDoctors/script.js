let doctorsData; // Variable to store the doctor data
let isDataLoaded = false; // Flag to track if data has been loaded

// Function to fetch and process the JSON data
function fetchDoctorsData() {
  fetch('doctors.json') // Assumes doctors.json is in the same folder
    .then(response => response.json())
    .then(data => {
      doctorsData = data;
      console.log('Data loaded successfully:', doctorsData);
      isDataLoaded = true; // Set the flag to true after data is loaded
      enableFindDoctorButton();
    })
    .catch(error => console.error('Error fetching data:', error));
}

// Function to enable the "Find Doctor" button after data is loaded
function enableFindDoctorButton() {
  const findDoctorButton = document.getElementById('findDoctorButton');
  findDoctorButton.disabled = false;
}

// Function to resize the text area based on content
function resizeTextArea(textArea) {
  textArea.style.height = 'auto';
  textArea.style.height = textArea.scrollHeight + 'px';
}

// Function to find and display the doctor information
function findDoctor() {
  if (!isDataLoaded || !doctorsData) {
    console.log('Data is still loading...');
    return; // Abort the search if data is not loaded or is empty
  }

  const doctorNameInput = document.getElementById('doctorNameInput').value.trim().toLowerCase();

  const doctorRecord = Object.values(doctorsData).find(doctor =>
    doctor.Name.some(name => name.toLowerCase() === doctorNameInput)
  );

  resetTextBoxes(); // Clean all existing information

  if (doctorRecord) {
    document.getElementById('nameTextbox').value = doctorRecord.Name[0];
    document.getElementById('linkTextbox').value = doctorRecord.Link[0];
    document.getElementById('addressTextbox').value = doctorRecord.Address[0];
    document.getElementById('hospitalAffiliationsTextbox').value =
      doctorRecord['Hospital Affiliations'] && doctorRecord['Hospital Affiliations'][0];

    // Resize the education & experience text area
    const educationTextArea = document.getElementById('educationTextbox');
    educationTextArea.value = doctorRecord['Education & Experience'].join('\n');
    resizeTextArea(educationTextArea);

    // Resize the certifications & licensure text area
    const certificationsTextArea = document.getElementById('certificationsTextbox');
    certificationsTextArea.value = doctorRecord['Certifications & Licensure'].join('\n');
    resizeTextArea(certificationsTextArea);
  } else {
    alert('Doctor not found in the database.');
  }
}

// Function to reset the text boxes
function resetTextBoxes() {
  document.getElementById('nameTextbox').value = '';
  document.getElementById('linkTextbox').value = '';
  document.getElementById('addressTextbox').value = '';
  document.getElementById('hospitalAffiliationsTextbox').value = '';
  document.getElementById('educationTextbox').value = '';
  document.getElementById('certificationsTextbox').value = '';
}

// Event listener for the input change on education & experience text area
document.getElementById('educationTextbox').addEventListener('input', function (event) {
  resizeTextArea(event.target);
});

// Event listener for the input change on certifications & licensure text area
document.getElementById('certificationsTextbox').addEventListener('input', function (event) {
    resizeTextArea(event.target);
  });

// Event listener for the "Find Doctor" button click
document.getElementById('findDoctorButton').addEventListener('click', findDoctor);

// Call the function to fetch the data when the page loads
document.addEventListener('DOMContentLoaded', fetchDoctorsData);
