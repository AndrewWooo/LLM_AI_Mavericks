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
        this.doctor1 = null;
        this.doctor2 = null;
        this.doctor3 = null;
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
        var acc = document.getElementsByClassName("accordion");
        var i;
        for (i = 0; i < acc.length; i++) {
            acc[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var panel = this.nextElementSibling;
                if (panel.style.maxHeight) {
                panel.style.maxHeight = null;
                } else {
                panel.style.maxHeight = panel.scrollHeight + "px";
                } 
            });
        }
    }
    toggleDoctorInfo(){
        const doctorInfoBox = document.getElementById('accordionBox');
        if(doctorInfoBox.style.opacity == 1){
            doctorInfoBox.style.opacity = 0;
        }else if(doctorInfoBox.style.opacity == 0){
            doctorInfoBox.style.opacity = 1;
        }
        /*
        doctorInfoBox.animate([{ opacity: '1' },{ opacity: '1' },{ opacity: '1' }, { opacity: '1' },{ opacity: '0' }], {
            duration: 1000000, // Duration of the animation (in milliseconds)
            iterations: 1, // Number of times the animation should run (1 means one time)
            easing: 'ease', // Timing function (optional, default is 'ease')
            fill: 'forwards', // Stay at the final keyframe after the animation (optional)
        });*/
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
            //document.getElementById('inputDate').disabled =true; // disable the date input
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
            duration: 3000, // Duration of the animation (in milliseconds)
            iterations: 2, // Number of times the animation should run (1 means one time)
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
                var calendarBox=`<input type="datetime-local" id="inputDate" min=${new Date().toISOString().slice(0, 16)}>`
                let msg4 = { name: "Mav", message: calendarBox };
                this.messages.push(msg4);
                this.updateChatText(chatbox)
                const dateInput=document.getElementById('inputDate');
                dateInput.addEventListener('change', () => {
                    this.selectedTime = new Date(dateInput.value);
                });
            }
            //if doctorList is not empty, then display the doctorList
            if (r.doctorList != null) {
                this.doctor1 = r.doctorList[0];
                this.doctor2 = r.doctorList[1];
                this.doctor3 = r.doctorList[2];
                var selectionBox = `<fieldset style="border: none;">
                <div><input type="checkbox" value="${this.doctor1['Name']}" class="doctorChoice"><label >${this.doctor1['Name']}</label></div>
                <div><input type="checkbox" value="${this.doctor2['Name']}" class="doctorChoice"><label >${this.doctor2['Name']}</label></div>
                <div><input type="checkbox" value="${this.doctor3['Name']}" class="doctorChoice"><label >${this.doctor3['Name']}</label></div></fieldset>
                `;
                let msg5 = { name: "Mav", message: selectionBox };
                this.messages.push(msg5);
                this.updateChatText(chatbox);
                this.fillInfo(1, this.doctor1);
                this.fillInfo(2, this.doctor2);
                this.fillInfo(3, this.doctor3);
                var acc = document.getElementsByClassName("accordion");
                var i;
                for (i = 0; i < acc.length; i++) {
                    if(i==0){
                        acc[i].textContent += this.doctor1['Name'];
                    }else if(i==1){
                        acc[i].textContent += this.doctor2['Name'];
                    }else{
                        acc[i].textContent += this.doctor3['Name'];
                    }
                }
                var doctorInfo = document.getElementById('accordionBox');
                doctorInfo.style.opacity = 1;
            }

        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
            this.sendButtonClicked = false;
          });
    }
    fillInfo(i, doctor){
        document.getElementById(`nameTB${i}`).value = doctor['Name'];
        document.getElementById(`linkTB${i}`).value = doctor['Link'];
        document.getElementById(`addressTB${i}`).value = doctor['Address'];
        document.getElementById(`hospitalTB${i}`).value = doctor['Hospital Affiliations'];
        var edu=document.getElementById(`educationTB${i}`);
        var cert=document.getElementById(`certificationsTB${i}`);
        if (doctor['Education & Experience'] != null){
            edu.placeholder = doctor['Education & Experience'];
        }else{
            edu.placeholder ='Missing Infomation';
        }
        if (doctor['Certifications & Licensure'] != null){    
           cert.placeholder= doctor['Certifications & Licensure'];
        }else{
            cert.placeholder ='Missing Infomation';
        }
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