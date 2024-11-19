import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const navigate = useNavigate();
    
    // States for registration
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    // States for checking the errors
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState(false);
    const [emailError, setEmailError] = useState("");
    const [passwordError, setPasswordError] = useState("");

    // Handling the name change
    const handleName = (e) => {
        setName(e.target.value);
        setSubmitted(false);
    };

    // Handling the email change with validation
    const handleEmail = (e) => {
        const emailValue = e.target.value;
        setEmail(emailValue);
        setSubmitted(false);

        // Email validation
        const emailRegex = /^[\w.-]+@[\w-]+\.[\w]{2,4}$/;
        if (!emailRegex.test(emailValue)) {
            setEmailError("Please enter a valid email");
        } else {
            setEmailError("");
        }
    };

    // Handling the password change with validation
    const handlePassword = (e) => {
        const passwordValue = e.target.value;
        setPassword(passwordValue);
        setSubmitted(false);

        // Password length validation
        if (passwordValue.length < 8) {
            setPasswordError("Password must be at least 8 characters long");
        } else {
            setPasswordError("");
        }
    };

    // Handling the form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (name === "" || email === "" || password === "" || emailError || passwordError) {
            setError(true);
        } else {
            
            const user = {
                name: name, 
                email: email,
                password: password,
            };

            try {
                const response = await fetch('http://localhost:8000/register',{
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(user),
                });
            if(!response.ok){
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            console.log(data);

            setSubmitted(true);
            setError(false);

            //redirect to login page
            navigate('/login');
            
            } catch (error){
                console.error('There was a problme with the fetch operation:', error);
                setError(true);
            }
        }
    };

    // Showing success message
    const successMessage = () => {
        return (
            <div className="success" style={{ display: submitted ? "" : "none" }}>
                <h1>User {name} successfully registered!</h1>
            </div>
        );
    };

    // Showing error message if error is true
    const errorMessage = () => {
        return (
            <div className="error" style={{ display: error ? "" : "none" }}>
                <h1>Please enter all the fields correctly</h1>
            </div>
        );
    };

    return (
        <div className="form">
            <div>
                <h1>User Registration</h1>
            </div>

            {/* Showing success and error messages */}
            <div className="messages">
                {errorMessage()}
                {successMessage()}
            </div>

            <form>
                {/* Name input */}
                <div>
                    <label className="label">Name</label>
                    <input onChange={handleName} className="input" value={name} type="text" />
                </div>

                {/* Email input */}
                <div>
                    <label className="label">Email</label>
                    <input onChange={handleEmail} className="input" value={email} type="email" />
                    <span className="error">{emailError}</span>
                </div>

                {/* Password input */}
                <div>
                    <label className="label">Password</label>
                    <input onChange={handlePassword} className="input" value={password} type="password" />
                    <span className="error">{passwordError}</span>
                </div>

                {/* Submit button */}
                <div>
                    <button onClick={handleSubmit} className="btn" type="submit">
                        Submit
                    </button>
                </div>
            </form>
        </div>
    );
};

export default Register;
