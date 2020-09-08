

function changeImage() {
    var styleFileImage = 'img/style/' + document.getElementById('style').value + '.jpg';
    console.log(document.getElementById('style').value);
    console.log(styleFileImage);
    document.getElementById('imageShow').src = "../static/" + styleFileImage;
}

function showStatus() {
    // document.getElementById('status').src = '../static/img/loading1.gif'
    var status = document.createElement('img');
    status.setAttribute('src','../static/img/loading1.gif')
    document.getElementById('status').appendChild(status)
}

$(".clickUpload").on("change","input[type='file']",function(){
	var filePath=$(this).val();
	if(filePath.indexOf("jpg")!=-1 || filePath.indexOf("png")!=-1){
		$(".fileerrorTip").html("").hide();
		var arr=filePath.split('\\');
		var fileName=arr[arr.length-1];
		$(".showFileName").html(fileName);
	}else{
		$(".showFileName").html("");
		$(".fileerrorTip").html("您未上传文件，或者您上传文件类型有误！").show();
		return false
	}
})

$(".picurlbtn").on("change","input[type='file']",function(){
    var filePath=$(this).val();
    if(filePath.indexOf("jpg")!=-1 || filePath.indexOf("jpeg")!=-1 || filePath.indexOf("png")!=-1){
        $("#picture_name").attr("value",filePath);
    }else{
		$("#picture_name").attr("value","仅支持jpg,jpeg,png格式！");
        return false
    }
})