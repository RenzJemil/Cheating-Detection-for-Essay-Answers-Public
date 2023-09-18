const msg = document.getElementsByClassName('flash-container');
const table_rows = document.getElementsByTagName('tr');
const backToTop = document.getElementById('back-to-top');

for (var i = 0; i < table_rows.length; i++) {
    if (i % 2 == 0) {
        table_rows[i].classList.add('even-row');
    }
    else {
        table_rows[i].classList.add('odd-row');
    }
}

function close_msg() {
    msg[0].style.display = 'none'
}

document.addEventListener('scroll', (e) => {
    console.log(window.scrollY);
    if (window.scrollY >= 300) {
        backToTop.style.display = 'block';
    }
    else
        backToTop.style.display = 'none';
});

const answersTable = document.getElementById('answers');
const answersHeading = document.getElementById('answers-heading');
answersHeading.style.display = 'none';
function showAnswers() {
    answersHeading.style.display = 'block';
    answersTable.classList.remove('table--invisible');
    answersTable.classList.add('table');
}
