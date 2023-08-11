class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button'),
            findDoctorButton: document.getElementById('findDoctor'),
        }
        this.sendButtonClicked = false;
        this.selectedTime = null;
        this.state = false;
        this.messages = [{ name: "Mav", message: "Hi, how do you do? What brought you here today?" }];
    }

    display() {
        const {openButton, chatBox, sendButton, findDoctorButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        findDoctorButton.addEventListener('click', () => this.toggleDoctorInfo())

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }
    toggleDoctorInfo(){
        const doctorInfoBox = document.querySelector('.doctorInfo');
        doctorInfoBox.style.opacity = 1;
        doctorInfoBox.animate([{ opacity: '1' },{ opacity: '1' },{ opacity: '1' }, { opacity: '1' },{ opacity: '0' }], {
            duration: 10000, // Duration of the animation (in milliseconds)
            iterations: 1, // Number of times the animation should run (1 means one time)
            easing: 'ease', // Timing function (optional, default is 'ease')
            fill: 'forwards', // Stay at the final keyframe after the animation (optional)
        });
    }
    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value;
        
        if(this.selectedTime){// if selectedTime is not null
            text1 = this.selectedTime.toLocaleString("en-US");
            this.selectedTime = null;
            //dateInput.type = 'hidden';
            document.getElementById('inputDate').disabled =true; // disable the date input
        }
        if (text1 === "" || this.sendButtonClicked) {
            return;
        }
        this.sendButtonClicked = true;
        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);
        this.updateChatText(chatbox);
        textField.value = ''
        var loader1 = document.getElementById('loader');
        loader1.animate([{ width: '0%', opacity:'0'},{ width: '25%', opacity:'0.5'}, { width: '50%', opacity:'1'},{ width: '75%', opacity:'1'},{ width: '60%', opacity:'0'}],{
            duration: 4000, // Duration of the animation (in milliseconds)
            iterations: 1, // Number of times the animation should run (1 means one time)
            easing: 'ease', // Timing function (optional, default is 'ease')
            fill: 'forwards', // Stay at the final keyframe after the animation (optional)
        });
        fetch('http://127.0.0.1:8080/chatOnline', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
              'Content-Type': 'application/json'
            },
          })
          .then(r => r.json())
          .then(r => {
            let msg2 = { name: "Mav", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            textField.value = ''
            this.sendButtonClicked = false; // enable the send button after the response is received
            // if r.additonalInfo is not empty, then display the additional info
            if (r.additionalInfo != null) {
                let msg3 = { name: "Mav", message: r.additionalInfo };
                this.messages.push(msg3);
                this.updateChatText(chatbox)
                textField.value = ''
            }
            // if calendar is needed, then display the calendar
            if (r.calendar !=null) {
                this.openCalendar();
            }

        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
            this.sendButtonClicked = false;
          });
    }
    openCalendar() {
        const dateInput = document.createElement('input');
        dateInput.type = 'datetime-local'; // Use 'datetime-local' input type to select both date and time
        dateInput.min = new Date().toISOString().slice(0, 16); // Set the minimum value to the current date and time
        dateInput.id="inputDate";
        dateInput.addEventListener('change', () => {
            this.selectedTime = new Date(dateInput.value);
            //alert('Date and time selected successfully!');
        });
        var node = document.getElementById('inputContent');
        // replace the input with the dateInput
        node.insertBefore(dateInput, node.childNodes[0]);
        // disable the date input
        document.getElementById('inputMsg').disabled =true;
        //hide the input
        document.getElementById('inputMsg').style.display = "none";
    }
      
    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "Mav")
            {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            }
            else
            {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
          });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}


const chatbox = new Chatbox();
chatbox.display();