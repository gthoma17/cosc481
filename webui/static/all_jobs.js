function jobTableInit(){
    initTableCols()
    $(".topts-box").click(function(argument){
        name = $(this).attr('id').split("-")[0]
        colClass = "." + name + "-col"
        boxId = "#" + name + "-box"
        $(colClass).toggle()
        toggleClass(boxId)
        modCookie(name)
    });
    $("#hide-topts").hide();
    $("#table-options").hide(); 
    $("#show-topts").click(function(){
        $("#show-topts").hide();
        $("#hide-topts").show();
        $("#table-options").slideDown("slow");   
    });
    $("#hide-topts").click(function(){
        $("#hide-topts").hide();
        $("#show-topts").show();
        $("#table-options").slideUp("slow");   
    });
}
function initTableCols(){
    hideCols = loadOrCreateCookie()
    updateBoxes(hideCols)
    updateCols()
}
function toggleClass (id) {
    if($(id).parent().hasClass("card-success")){
        $(id).parent().removeClass("card-success")
        $(id).parent().addClass("card-danger")
    }
    else{
        $(id).parent().removeClass("card-danger")
        $(id).parent().addClass("card-success")
    }
}
function loadOrCreateCookie () {
    if (Cookies.get('userHiddenCols') == undefined){
        console.log("Creating it")
        Cookies.set('userHiddenCols',"customer supervisor opened billed closed")
    }
    console.log(Cookies.get('userHiddenCols').split(" "))
    return Cookies.get('userHiddenCols').split(" ")
}
function updateBoxes (hideCols) {
    hideCols.forEach(uncheckBox)
}
function uncheckBox(element) {
    $('#'+element+'-box').prop('checked', false);
    toggleClass('#'+element+'-box')
}
function updateCols (){
    $(".topts-box").each(function(){
        if (!$(this).prop('checked')) {
            colClass = "." + $(this).attr('id').split("-")[0] + "-col"
            $(colClass).hide()
        };
    })
}
function modCookie(name) {
    cookieList = loadOrCreateCookie()
    if (jQuery.inArray( name, cookieList ) != -1) {
        console.log("removing "+name+" from cookie")
        cookieList.splice(cookieList.indexOf(name),1);
    }
    else{
        console.log("adding "+name+" to cookie")
        cookieList.push(name)
    };
    console.log("New cookie: ")
    console.log(cookieList)
    Cookies.set('userHiddenCols', cookieList.join(" "))
    
}
$(document).ready(function(){
    jobTableInit()
});