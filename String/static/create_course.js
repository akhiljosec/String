function create_video_fields(){
    var number = document.getElementById('video_count').value;
    var video_field = document.getElementById('video_field');

//    if (document.getElementById('link_count').value) {
//         prev_link_count = document.getElementById('link_count').value;
////         document.getElementById('disp').innerHTML=prev_link_count;
//    }

    video_field.innerHTML = "";

    for(var i=0; i<number; i++){
        let j = i+1
        var label = document.createElement("label");
        label.innerHTML = "Video" + j;
        var text_area = document.createElement("textarea");
        text_area.rows = '1';
        text_area.cols = '50';
        text_area.name = 'video'+j;
        video_field.appendChild(document.createElement("br"));
        video_field.appendChild(label);
        video_field.appendChild(document.createElement("br"));
        video_field.appendChild(text_area);
        video_field.appendChild(document.createElement("br"));
//        video_field.appendChild(document.createElement("br"));
    }

}



function update_video_fields(){
    var number = document.getElementById('video_count').value;
    var video_field = document.getElementById('video_field');

    video_field.innerHTML = "";
    prev_link_count = document.getElementById('link_count').value;
//         document.getElementById('disp').innerHTML=prev_link_count;
    for(var i=0; i<number; i++){
        let j = parseInt(prev_link_count)+i+1
        var label = document.createElement("label");
        label.innerHTML = "Video" + j;
        var text_area = document.createElement("textarea");
        text_area.rows = '1';
        text_area.cols = '50';
        text_area.name = 'video'+j;
        video_field.appendChild(document.createElement("br"));
        video_field.appendChild(label);
        video_field.appendChild(document.createElement("br"));
        video_field.appendChild(text_area);
        video_field.appendChild(document.createElement("br"));
//        video_field.appendChild(document.createElement("br"));
    }

}


function create_page_fields(){
    var number = document.getElementById('page_count').value;
    var page_field = document.getElementById('page_field');

    page_field.innerHTML = "";

    for(var i=0; i<number; i++){
        let j = i+1
        var label = document.createElement("label");
        label.innerHTML = "page" + j + "contents";
        var text_area = document.createElement("textarea");
        var video = document.createElement("textarea");
        text_area.rows = '5';
        text_area.cols = '80';
        text_area.name = 'description'+j;
        text_area.placeholder = 'Enter the Course Content'
        video.rows = '1';
        video.cols = '80';
        video.name = 'video'+j;
        video.placeholder = 'Enter the Video Link'
        page_field.appendChild(document.createElement("br"));
        page_field.appendChild(label);
        page_field.appendChild(document.createElement("br"));
        page_field.appendChild(video);
        page_field.appendChild(document.createElement("br"));
        page_field.appendChild(text_area);
        page_field.appendChild(document.createElement("br"));
//        video_field.appendChild(document.createElement("br"));
    }
}


