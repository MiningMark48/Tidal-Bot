// a key map of allowed keys
let allowedKeys = {
	37: 'left',
	38: 'up',
	39: 'right',
	40: 'down',
	65: 'a',
	66: 'b'
  };
  
  // Konami Code sequence
  let konamiCode = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right', 'b', 'a'];
//   let konamiCode = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right'];
  
  // A letiable to remember the 'position' the user has reached so far.
  let konamiCodePosition = 0;
  
  // Add keydown event listener
  document.addEventListener('keydown', function(e) {
	// Get the value of the key code from the key map
	let key = allowedKeys[e.keyCode];
	// Get the value of the required key from the konami code
	let requiredKey = konamiCode[konamiCodePosition];
  
	// Compare the key with the required key
	if (key == requiredKey) {
  
	  // Move to the next key in the konami code sequence
	  konamiCodePosition++;
  
	  // If the last key is reached, activate cheats
	  if (konamiCodePosition == konamiCode.length) {
		activateCheats();
		konamiCodePosition = 0;
	  }
	} else {
	  konamiCodePosition = 0;
	}
  });

  function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  async function activateCheats() {
	console.log("KONAMI");

	let defaultColor = document.body.style.backgroundColor;
	
	let audio = new Audio('audio/airhorn.mp3');
	audio.play();
	
	for (let i = 0; i < 8; i++) {
		document.body.style.backgroundColor = "#000000";	
		await sleep(100);
		document.body.style.backgroundColor = "#ffffff";
		await sleep(100);
	}

	document.body.style.backgroundColor = defaultColor;
  }