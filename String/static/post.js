function show_post_writer(){
    document.post_form.style.display = 'block';
}


function hide_post_writer(){
    document.post_form.style.display = 'none';
}


function post_content() {
  var x = document.getElementById("post_id");
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}