(function() {
    const timerContainer = document.getElementById('timer');
    const timerDisplay = document.getElementById('timerDisplay');
    const form = document.getElementById('assessmentForm');
    let timeRemaining = parseInt(timerContainer.dataset.timeRemaining);

    function updateDisplay() {
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        timerDisplay.textContent = String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');

        if (timeRemaining <= 60) {
            timerContainer.classList.remove('bg-gray-700');
            timerContainer.classList.add('bg-red-600/30');
            timerDisplay.classList.remove('text-white');
            timerDisplay.classList.add('text-red-400');
        }
    }

    function tick() {
        if (timeRemaining <= 0) {
            timerDisplay.textContent = '00:00';
            form.submit();
            return;
        }
        timeRemaining--;
        updateDisplay();
    }

    updateDisplay();
    setInterval(tick, 1000);
})();
