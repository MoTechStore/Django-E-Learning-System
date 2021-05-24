$(".next1").on("click", function () {
	if (validate1()) {
		$('.active').next().addClass('active');
		$('.f1').hide();
		$('.f2').show();
	} else {
		$('#notify1').html('Fill up the entry first!!');
	}
});

$(".next2").on("click", function () {
	if (validate2()) {
		$('.active').next().addClass('active');
		$('.f1').hide();
		$('.f2').hide();
		$('.f3').show();
	}

});

$(".previous1").on("click", function () {
	$('.active').next().removeClass('active');
	$('.f1').show();
	$('.f2').hide();
});

$(".previous2").on("click", function () {
	$('.active').next().next().removeClass('active');
	$('.f3').hide();
	$('.f2').show();
});


$(".submit").on("click", function () {
	if (validate3()) {
		$('.previous2').fadeOut(500);
		$('.submit').fadeOut(500);
		$('#notify3').html('Successfully Submitted');
	}

});

function validate1() {
	var fname, lname, contact;
	fname = $(".fname").val();
	lname = $(".lname").val();
	contact = $(".contact").val();
	if (fname === '' || lname === '' || contact === '') {
		return false;
	}
	return true;
}

function validate2() {
	var fname, lname, contact;
	twitter = $("#twitter").val();
	fb = $("#fb").val();
	insta = $("#insta").val();
	var filter = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
	if (twitter === '' && fb === '' && insta === '') {
		$('#notify2').html('You must enter atleast one social profile email!!');
		return false;
	}
	if ((!filter.test(twitter)) && (!filter.test(fb)) && (!filter.test(fb))) {
		$('#notify2').html('Enter valid email');
		return false;
	}

	return true;
}

function validate3() {
	var email, pswd, cpswd;
	email = $('.email').val();
	pswd = $('.pswd').val();
	cpswd = $('.cpswd').val();
	var filter = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
	if (!filter.test(email)) {
		$('#notify3').html('Enter valid email');
		return false;
	}
	if (pswd !== cpswd) {
		$('#notify3').html('Not confirm yet!');
		return false;
	}
	if (pswd === '' || cpswd === '') {
		$('#notify3').html('Enter the password');
		return false;
	}
	return true;
}
