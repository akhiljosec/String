function password_validation(){
    var password = document.sign_up_form.password.value;
    var confirm_password = document.sign_up_form.confirm_password.value;

    if (password==confirm_password){
        document.getElementById('pwd').innerHTML="Password Matched";
        document.getElementById('button').disabled = false;
        return true;
    }
    else{
        document.getElementById('pwd').innerHTML="Password didn't Matched";
        document.getElementById('button').disabled = true;
        return false;
    }
}


function subject_selector(){
    var user_type = document.sign_up_form.user_type.value;
    document.getElementById('pwd').innerHTML=user_type;
    if (user_type=='instructor'){
        document.getElementById('subject').disabled = false;
        return true;
    }
    else{
        document.getElementById('subject').disabled = true;
        return false;
    }
}


//function validatePhone(){
//    var pnum = document.sign_up_form.pnum.value;
//    if (pnum.length==10 && isNumeric(pnum)) {
//        document.getElementById('pnum').innerHTML="Phone Number is valid";
//        document.getElementById('button').disabled = false;
//        return true
//    }
//    else {
//        document.getElementById('pnum').innerHTML="Phone Number is not valid";
//        document.getElementById('button').disabled = true;
//        validatePhone(num);
//    }
//}
