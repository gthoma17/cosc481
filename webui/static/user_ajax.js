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
});
function flashRedBackground (div) {
    bg = div.css("background");
    div.css("background", "red");
    setTimeout(function(){
        div.css("background", bg);
    }, 2000);
}
function userAjax(divLLQ){
    nameDivId = "#name";
    titleDivId = "#title";
    emailDivId = "#email";
    adminDivId = "#admin";
    numbersDivId = "#numbers";
    postUrl = "/forward/user"
    if (divLLQ != null){
        nameDivId = nameDivId.concat("_edit_", divLLQ);
        titleDivId = titleDivId.concat("_edit_", divLLQ);
        emailDivId = emailDivId.concat("_edit_", divLLQ);
        adminDivId = adminDivId.concat("_edit_", divLLQ);
        numbersDivId = numbersDivId.concat("_edit_", divLLQ);
        postUrl = "/forward/user/"+divLLQ
    };
    //validate the form
    if ($(nameDivId).val() != "" && $(titleDivId).val() != "select" && $(emailDivId).val() != "") {
        postData = {}
        postData.name = $(nameDivId).val()
        postData.title = $(titleDivId).val()
        postData.email = $(emailDivId).val()
        postData.isAdmin = $(adminDivId).prop("checked")
        postData.canSeeNumbers = $(numbersDivId).prop("checked")
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
                    console.log("Unsuccessful add")
                    //console.log(response)
                    //response contained non numerics. Something bad happened
                    $("#apiResponse").html(response)
                };
              
            }
        });    
    }
    else{
        //didn't validate. Tell user where they goofed
        if ($(nameDivId).val() == "") {
            flashRedBackground($(nameDivId));
        };
        if ($(titleDivId).val() == "select") {
            flashRedBackground($(titleDivId));
        };
        if ($(emailDivId).val() == "") {
            flashRedBackground($(emailDivId));
        };
    };        
}
function newUserRow(userId){
    rowTemplate = $("#userRowTemplate").html();
    newRow = replaceAllSubsting(rowTemplate, "!template!", userId);
    $(newRow).insertBefore("#addUserForm");
     //add new values to the row
    $("#name_".concat(userId)).text($("#name").val());
    $("#title_".concat(userId)).text($("#title").val());
    $("#email_".concat(userId)).text($("#email").val());
    if($("#admin").prop('checked')){
        $("#admin_".concat(userId)).text("Yes")
    }
    else{
        $("#admin_".concat(userId)).text("No")
    };
    if($("#numbers").prop('checked')){
        $("#numbers_".concat(userId)).text("Yes")
    }
    else{
        $("#numbers_".concat(userId)).text("No")
    };
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
    newRow = replaceAllSubsting(rowTemplate, "!template!", itemId);
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
    $("#title_".concat(userId)).text($("#title_edit_".concat(userId)).val());
    $("#email_".concat(userId)).text($("#email_edit_".concat(userId)).val());
    if ($("#admin_edit_".concat(userId)).attr('checked')) {
        console.log("admin checked")
        $("#admin_".concat(userId)).text("Yes")
    } else{
        $("#admin_".concat(userId)).text("No")
    };
    if ($("#numbers_edit_".concat(userId)).attr('checked')) {
        $("#numbers_".concat(userId)).text("Yes")
    } else{
        $("#numbers_".concat(userId)).text("No")
    };
    hideEditCols(userId);
}
function showEditCols (userId) {
    //show the edit cols
    $("#name_edit_".concat(userId)).show()
    $("#title_edit_".concat(userId)).show()
    $("#email_edit_".concat(userId)).show()
    $("#admin_edit_".concat(userId)).show()
    $("#numbers_edit_".concat(userId)).show()
    $("#buttons_edit_".concat(userId)).show()
    //hide the display cols
    $("#name_".concat(userId)).hide()
    $("#title_".concat(userId)).hide()
    $("#email_".concat(userId)).hide()
    $("#admin_".concat(userId)).hide()
    $("#numbers_".concat(userId)).hide()
    $("#buttons_".concat(userId)).hide()
}
function resetEditCols (userId) {
    //set text fields
    $("#name_edit_".concat(userId)).val($("#name_".concat(userId)).text())
    $("#email_edit_".concat(userId)).val($("#email_".concat(userId)).text())
    //set the select properly
    $("#title_edit_".concat(userId)).val($("#title_".concat(userId)).text())
    //set checkboxes properly
    if ($("#admin_".concat(userId)).text() == "Yes") {
        console.log("Checking")
        $("#admin_edit_".concat(userId)).prop('checked', true);
    } else{
        $("#admin_edit_".concat(userId)).prop('checked', false);
    };
    if ($("#numbers_".concat(userId)).text() == "Yes") {
        $("#numbers_edit_".concat(userId)).prop('checked', true);
    } else{
        $("#numbers_edit_".concat(userId)).prop('checked', false);
    };
}
function hideEditCols (userId){
    //hide the edit cols
    $("#name_edit_".concat(userId)).hide()
    $("#title_edit_".concat(userId)).hide()
    $("#email_edit_".concat(userId)).hide()
    $("#admin_edit_".concat(userId)).hide()
    $("#numbers_edit_".concat(userId)).hide()
    $("#buttons_edit_".concat(userId)).hide()
    //show the display cols
    $("#name_".concat(userId)).show()
    $("#title_".concat(userId)).show()
    $("#email_".concat(userId)).show()
    $("#admin_".concat(userId)).show()
    $("#numbers_".concat(userId)).show()
    $("#buttons_".concat(userId)).show()
}
function clearAddForm(){
    $("#name").val("");
    $("#title").val("select");
    $("#email").val("");
    $("#admin" ).attr('checked', false);
    $("#numbers").attr('checked', false);
}
function replaceAllSubsting (str, oldSubStr, newSubStr) {
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
    })
}