$(document).ready(function(){
    initializeButtonListeners();
    $("#addUserForm").hide();
    $(".edit_row").hide();
    $("#cancelUserAdd").click(function(){
        clearAddForm()
        $("#addUserForm").hide();
        $("#showUserAdd").show();
    });
    $("#showUserAdd").click(function(){
        $("#addUserForm").show()
        $("#showUserAdd").hide()
    });
    $("#userAdd").click(function(){
        userAjax()
    });
    $("[id^=delete_]").click(function(){
        buttonId = $(this).attr('id').split("_")
        userId = buttonId[buttonId.length -1]
        postData = {}
        postData.id = userId
        $.ajax({
            url : "/forward/delete/user",
            dataType:"text",
            method:"POST",
            data: JSON.stringify(postData),
            success:function(response){
                if (apiResponseIsGood(response)) {
                    console.log("Successful delete")
                    console.log(postData)
                    console.log(response)
                    $("#user".concat(userId)).remove()
                } else {
                    console.log("Unsuccessful delete")
                    $("#apiResponse").html(response)
                };
            }
        });
    });
});
function apiResponseIsGood(response){
    pattStr1 = "^2\\d\\d.*"
    pattStr2 = "^[0-9]*$"
    var pattern1 = new RegExp(pattStr1)
    var pattern2 = new RegExp(pattStr2)
    test1 = pattern1.test(response)
    test2 = pattern2.test(response)
    result = test1 || test2
    console.log(result)
    return result
}
function flashRedBackground (div) {
    bg = div.css("background");
    div.css("background", "red");
    setTimeout(function(){
        div.css("background", bg);
    }, 2000);
}
function userAjax(divLLQ){
    nameDivId = "#name";
    permDivId = "#permissionLevel";
    emailDivId = "#email";
    phoneDivId = "#phone";
    postUrl = "/forward/user"
    if (divLLQ != null){
        nameDivId = nameDivId.concat("_edit_", divLLQ);
        permDivId = permDivId.concat("_edit_", divLLQ);
        emailDivId = emailDivId.concat("_edit_", divLLQ);
        phoneDivId = phoneDivId.concat("_edit_", divLLQ);
        postUrl = "/forward/user/"+divLLQ
    };
    //validate the form
    if ($(nameDivId).val() != "" && $(permDivId).val() != "select" && $(permDivId).val() != "" && $(emailDivId).val() != "" && $(phoneDivId).val() != "") {
        postData = {}
        postData.name = $(nameDivId).val()
        postData.permissionLevel = $(permDivId).val()
        postData.email = $(emailDivId).val()
        postData.phone = $(phoneDivId).val()
        $.ajax({
            url : postUrl,
            dataType:"text",
            method:"POST",
            data: JSON.stringify(postData),
            success:function(response){
                allowedResponses = [
                    "202 User Updated"
                ]
                if (/^\d+$/.test(response) || (allowedResponses.indexOf(response) > -1)) {
                    console.log("Successful add")
                    //respone was only integers, adding was successful
                    if (divLLQ != null){
                        //we're editing
                        updateUserRow(divLLQ)
                    }
                    else{
                        //we're adding
                        newUserRow(response);
                    };
                } else{
                    console.log("Unsuccessful add" + response)
                    //console.log(response)
                    //response contained non numerics. Something bad happened
                    $("#apiResponse").html(response)
                };
              
            }
        });    
    }
    else{
        console.log("Here:")
        console.log($(nameDivId).val())
        console.log($(permDivId).val())
        console.log($(emailDivId).val())
        console.log($(phoneDivId).val())
        //didn't validate. Tell user where they goofed
        if ($(nameDivId).val() == "") {
            flashRedBackground($(nameDivId));
        };
        if ($(permDivId).val() == "select" && $(permDivId).val() != undefined)  {
            console.log("Lame")
            flashRedBackground($(permDivId));
        };
        if ($(emailDivId).val() == "") {
            flashRedBackground($(emailDivId));
        };
        if ($(phoneDivId).val() == "") {
            flashRedBackground($(phoneDivId));
        };
    };        
}
function newUserRow(userId){
    rowTemplate = $("#userRowTemplate").html();
    newRow = replaceAllSubstring(rowTemplate, "!template!", userId);
	$("#adminTbody").append(newRow);
    //$(newRow).insertBefore("#addUserForm");
     //add new values to the row
    $("#name_".concat(userId)).text($("#name").val());
    $("#perm_".concat(userId)).text($("#permissionLevel").val());
    $("#email_".concat(userId)).text($("#email").val());
    $("#phone_".concat(userId)).text($("#phone").val());
    resetEditCols(userId) //set edit column values equal to display columns
    hideEditCols(userId)
    clearAddForm()
    initializeButtonListeners()
}
function updateUserRow(userId){
    updateDisplayCols(userId);
    hideEditCols(userId);
}
function newBudgetItemRow(itemId){
    //create new row from template
    rowTemplate = $("#budgetRowTemplate").html()
    newRow = replaceAllSubstring(rowTemplate, "!template!", itemId);
    $(newRow).insertBefore("#addItemForm");
    //add new values to the row
    $("#name_".concat(itemId)).text($("#name").val());
    $("#type_".concat(itemId)).text($("#type").val());
    $("#cost_".concat(itemId)).text($("#cost").val());
    //hide edit options initially
    $("#name_edit_".concat(itemId)).hide()
    $("#type_edit_".concat(itemId)).hide()
    $("#cost_edit_".concat(itemId)).hide()
    $("#buttons_edit_".concat(itemId)).hide()
    //empty the form
    $("#name").val("");
    $("#type").val("select");
    $("#cost").val("");
}
function updateDisplayCols (userId) {
    //move new values into display cols
    console.log("updating row")
    $("#name_".concat(userId)).text($("#name_edit_".concat(userId)).val());
    $("#permissionLevel_".concat(userId)).text($("#permissionLevel_edit_".concat(userId)).val());
    $("#email_".concat(userId)).text($("#email_edit_".concat(userId)).val());
    $("#phone_".concat(userId)).text($("#phone_edit_".concat(userId)).val());
}
function showEditCols (userId) {
    //show the edit cols
    $("#name_edit_".concat(userId)).show()
    $("#permissionLevel_edit_".concat(userId)).show()
    $("#email_edit_".concat(userId)).show()
    $("#phone_edit_".concat(userId)).show()
    $("#buttons_edit_".concat(userId)).show()
    //hide the display cols
    $("#name_".concat(userId)).hide()
    $("#permissionLevel_".concat(userId)).hide()
    $("#email_".concat(userId)).hide()
    $("#phone_".concat(userId)).hide()
    $("#buttons_".concat(userId)).hide()
}
function resetEditCols (userId) {
    //set text fields
    $("#name_edit_".concat(userId)).val($("#name_".concat(userId)).text())
    $("#email_edit_".concat(userId)).val($("#email_".concat(userId)).text())
    $("#phone_edit_".concat(userId)).val($("#phone_".concat(userId)).text())
    //set the select properly
    $("#permissionLevel_edit_".concat(userId)).val($("#permissionLevel_".concat(userId)).text())
}
function hideEditCols (userId){
    //hide the edit cols
    $("#name_edit_".concat(userId)).hide()
    $("#permissionLevel_edit_".concat(userId)).hide()
    $("#email_edit_".concat(userId)).hide()
    $("#phone_edit_".concat(userId)).hide()
    $("#buttons_edit_".concat(userId)).hide()
    //show the display cols
    $("#name_".concat(userId)).show()
    $("#permissionLevel_".concat(userId)).show()
    $("#email_".concat(userId)).show()
    $("#phone_".concat(userId)).show()
    $("#buttons_".concat(userId)).show()
}
function clearAddForm(){
    $("#name").val("");
    $("#permissionLevel").val("select");
    $("#email").val("");
    $("#phone").val("");
}
function replaceAllSubstring (str, oldSubStr, newSubStr) {
    return str.split(oldSubStr).join(newSubStr);
}
function initializeButtonListeners(){
    $(".edit_button").click(function(){
        //hide all display cols, show all edit cols
        buttonId = $(this).attr('id').split("_")
        userId = buttonId[buttonId.length -1]
        resetEditCols(userId)
        showEditCols(userId)
    });
    $(".cancel_button").click(function(){
        //hide all display cols, show all edit cols
        buttonId = $(this).attr('id').split("_")
        userId = buttonId[buttonId.length -1]
        hideEditCols(userId);
        resetEditCols(userId);
    });
    $(".save_button").click(function(){
        buttonId = $(this).attr('id').split("_")
        userId = buttonId[buttonId.length -1]
        userAjax(userId)
    });
	$("[id^=delete_]").click(function(){
        buttonId = $(this).attr('id').split("_")
        userId = buttonId[buttonId.length -1]
        postData = {}
        postData.id = userId
        $.ajax({
            url : "/forward/delete/user",
            dataType:"text",
            method:"POST",
            data: JSON.stringify(postData),
            success:function(response){
                if (apiResponseIsGood(response)) {
                    console.log("Successful delete")
                    console.log(postData)
                    console.log(response)
                    $("#user".concat(userId)).remove()
                } else {
                    console.log("Unsuccessful delete")
                    $("#apiResponse").html(response)
                };
            }
        });
    });
}