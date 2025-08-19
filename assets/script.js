// === Dynamically Load particles.min.js THEN Initialize ===
document.addEventListener('DOMContentLoaded', function () {
    // Create <script> to load particles.min.js
    const particlesScript = document.createElement('script');
    particlesScript.src = '/assets/particles.min.js';

    // Once particles.min.js is loaded, run particlesJS
    particlesScript.onload = function () {
        particlesJS("particles-js", {
            "particles": {
                "number": {
                    "value": 50,
                    "density": {
                        "enable": true,
                        "value_area": 800
                    }
                },
                "color": {
                    "value": "#00ffe1"
                },
                "shape": {
                    "type": "circle"
                },
                "opacity": {
                    "value": 0.4
                },
                "size": {
                    "value": 3
                },
                "line_linked": {
                    "enable": true,
                    "distance": 150,
                    "color": "#00ffe1",
                    "opacity": 0.2,
                    "width": 1
                },
                "move": {
                    "enable": true,
                    "speed": 2
                }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": {
                    "onhover": {
                        "enable": true,
                        "mode": "grab"
                    }
                },
                "modes": {
                    "grab": {
                        "distance": 140,
                        "line_linked": {
                            "opacity": 0.5
                        }
                    }
                }
            },
            "retina_detect": true
        });
    };

    // Append to head
    document.head.appendChild(particlesScript);
});
