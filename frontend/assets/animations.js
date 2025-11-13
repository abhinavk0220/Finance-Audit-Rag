document.addEventListener("DOMContentLoaded", function() {
  
  // Bubble animation
  const bubbles = document.querySelectorAll(".chat-bubble");
  bubbles.forEach((b, i) => {
    b.style.opacity = 0;
    // Set transform start state for the animation
    b.style.transform = "translateY(15px)"; 
    b.style.transition = "opacity 0.6s ease, transform 0.5s ease";
    setTimeout(() => {
      b.style.opacity = 1;
      b.style.transform = "translateY(0)";
    }, 200 * i);
  });

  // Button click animation
  const btns = document.querySelectorAll("button");
  btns.forEach(btn => {
    btn.addEventListener("click", () => {
      btn.style.transform = "scale(0.97)";
      setTimeout(() => (btn.style.transform = "scale(1)"), 100);
    });
  });

});