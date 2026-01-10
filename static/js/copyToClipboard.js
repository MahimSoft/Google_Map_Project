function showCustomAlert(message) {
  const alertElement = document.getElementById("customAlert");
  alertElement.innerHTML = message;
  alertElement.style.display = "block"; // Show the alert

  setTimeout(() => {
    alertElement.style.display = "none"; // Hide the alert after 5 seconds
  }, 3000); // 5000 milliseconds = 5 seconds
}

function changeColor(ele, color1, color2) {
  ele.addEventListener("mouseover", () => {
    ele.style.position = "relative";
    ele.style.zIndex = "1";
    ele.style.color = color1; // e.g., '#f0f0f0'
  });
  ele.addEventListener("mouseout", () => {
    ele.style.zIndex = "0";
    ele.style.color = color2; // e.g., 'white'
  });
}

function copyElementText(id, extractText = false, split_text = "---") {
  var copyText = document.getElementById(id);
  var textToCopy = copyText.innerText;
  try {
    var tooltipText = document.getElementById(
      `tooltipid${id.slice(3)}`
    ).innerText;
    textToCopy = textToCopy.replace(tooltipText, "");
    textToCopy = textToCopy.replace("\n", "");
    if (extractText) {
      textToCopy = textToCopy.split(split_text)[1];
    }
  } catch (err) {
    alert("Failed to copy with fallback: " + err);
  }

  const showSuccess = () => {
    showCustomAlert(
      `<h6 class="text-center rounded-md p-3 -m-2.5 bg-gradient-to-r from-blue-500 via-gray-500 to-green-700 z-n1"> ${textToCopy}<span style='color:red;'>  --- Copied!</span></h6>`
    );
  };

  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(textToCopy).then(showSuccess, (err) => {
      alert("Failed to copy: " + err);
    });
  } else {
    // Fallback for insecure contexts
    const textArea = document.createElement("textarea");
    textArea.value = textToCopy;
    textArea.style.position = "fixed";
    textArea.style.left = "-9999px";
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand("copy");
      showSuccess();
    } catch (err) {
      alert("Failed to copy with fallback: " + err);
    }
    document.body.removeChild(textArea);
  }
}
function addIdEventListenerTo_dd(
  tag_or_class = "dd",
  color_change = true,
  extractText = false,
  split_text = "---",
  use_class = false
) {
  if (use_class) {
    var ddEle = document.getElementsByClassName(tag_or_class);
  } else {
    var ddEle = document.getElementsByTagName(tag_or_class);
  }

  // let ddEle = document.getElementsByTagName(dd);
  for (let i = 0; i < ddEle.length; i++) {
    ddEle[i].id = `txt${i}`;
    ddEle[i].addEventListener("click", function () {
      copyElementText(this.id, extractText, split_text);
    });
    let textOriginal = ddEle[i].innerHTML;
    ddEle[i].innerHTML = ` 
        <span class="tooltip_w3s">
        ${textOriginal}
        <span id="tooltipid${i}" class="tooltiptext_w3s">Click to copy!</span>
        </span>`;
    if (color_change) {
      ddEle[i].style.backgroundColor = "#F0F8FF";
      ddEle[i].style.color = "#008000";
      changeColor(ddEle[i], "#458B00", "#008000");
      // ddEle[i].style.transition = 'color 0.3s ease';
    }
  }
}
