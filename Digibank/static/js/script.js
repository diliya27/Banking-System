document.addEventListener("DOMContentLoaded", function () {
    emailjs.init("r6s-hc8rzbW7P81ZA"); // Your public key

    document.getElementById("contact-form").addEventListener("submit", function (event) {
        event.preventDefault(); // Stop form from reloading the page

        let parms = {
            name: document.getElementById("name").value,
            email: document.getElementById("email").value,
            subject: document.getElementById("subject").value,
            message: document.getElementById("message").value,
        };

        document.getElementById("send-button").innerText = "Sending...";

        emailjs
            .send("service_4mr5tto", "template_16lgxmz", parms)
            .then(function (response) {
                alert("Email sent successfully!");
                document.getElementById("contact-form").reset();
                document.getElementById("send-button").innerText = "Send Message";
            })
            .catch(function (error) {
                console.error("Failed to send email", error);
                alert("Failed to send mail. Please try again.");
                document.getElementById("send-button").innerText = "Send Message";
            });
    });
});
