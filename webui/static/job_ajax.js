$(document).ready(function(){
    $("#addItemForm").hide();
    $(".edit_row").hide();
    $("#cancelBudgetAdd").click(function(){
        $("#name").val("");
        $("#type").val("select");
        $("#cost").val("");
        $("#addItemForm").hide()
        $("#showBudgetAdd").show()
    });
    $("#showBudgetAdd").click(function(){
        $("#addItemForm").show()
        $("#showBudgetAdd").hide()
    });
    $("#budgetAdd").click(function(){
        budgetItemAjax()
    });
    $(".edit_button").click(function(){
        //hide all display cols, show all edit cols
        buttonId = $(this).attr('id').split("_")
        itemId = buttonId[buttonId.length -1]
        //show the edit cols
        console.log("Show " + "#name_edit_".concat(itemId))
        $("#name_edit_".concat(itemId)).show()
        $("#type_edit_".concat(itemId)).show()
        $("#cost_edit_".concat(itemId)).show()
        $("#buttons_edit_".concat(itemId)).show()
        //hide the display cols
        $("#name_".concat(itemId)).hide()
        $("#type_".concat(itemId)).hide()
        $("#cost_".concat(itemId)).hide()
        $("#buttons_".concat(itemId)).hide()
        //set the select properly
        $("#type_edit_".concat(itemId)).val($("#type_".concat(itemId)).text())
    });
    $(".cancel_button").click(function(){
        //hide all display cols, show all edit cols
        buttonId = $(this).attr('id').split("_")
        itemId = buttonId[buttonId.length -1]
        //hide the edit cols
        $("#name_edit_".concat(itemId)).hide()
        $("#type_edit_".concat(itemId)).hide()
        $("#cost_edit_".concat(itemId)).hide()
        $("#buttons_edit_".concat(itemId)).hide()
        //show the display cols
        $("#name_".concat(itemId)).show()
        $("#type_".concat(itemId)).show()
        $("#cost_".concat(itemId)).show()
        $("#buttons_".concat(itemId)).show()
        //reset the edit rows
        $("#name_edit_".concat(itemId)).val($("#name_".concat(itemId)).text());
        $("#type_edit_".concat(itemId)).val($("#type_".concat(itemId)).text());
        $("#cost_edit_".concat(itemId)).val($("#cost_".concat(itemId)).text());
    });

});
function flashRedBackground (div) {
    bg = div.css("background");
    div.css("background", "red");
    setTimeout(function(){
        div.css("background", bg);
    }, 2000);
}
function budgetItemAjax(divLLQ){
    nameDivId = "#name";
    typeDivId = "#type";
    costDivId = "#cost";
    if (divLLQ != null){
        nameDivId = nameDivId.concat(divLLQ);
        typeDivId = typeDivId.concat(divLLQ);
        costDivId = costDivId.concat(divLLQ);
    };
    //validate the form
    if ($(nameDivId).val() != "" && $(typeDivId).val() != "select" && $(costDivId).val() != "") {
        postData = {}
        postData.job_id = $("#jobId").text()
        postData.apiKey = $("#apiKey").text()
        postData.name = $(nameDivId).val()
        postData.type = $(typeDivId).val()
        postData.cost = $(costDivId).val()
        $.ajax({
            url : "/forward/budgetItem",
            dataType:"text",
            method:"POST",
            data: JSON.stringify(postData),
            success:function(response){
              if (/^\d+$/.test(response)) {
                console.log("Successful add")
                //respone was only integers, adding was successful
                if (divLLQ != null){
                    //we're editing
                    updateBudgetItemRow(divLLQ)
                }
                else{
                    //we're adding
                    newBudgetItemRow(response);
                };
              } else{
                console.log("Unsuccessful add")
                console.log(data)
                //response contained non numerics. Something bad happened
                $("#apiResponse").html(data)
              };
              
            }
        });    
    }
    else{
        //didn't validate. Tell user where they goofed
        if ($("#name").val() == "") {
            flashRedBackground($("#name"));
        };
        if ($("#type").val() == "select") {
            flashRedBackground($("#type"));
        };
        if ($("#cost").val() == "") {
            flashRedBackground($("#cost"));
        };
    };        
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
function updateBudgetItemRow (itemId) {
    //move new values into display cols
    $("#name_".concat(itemId)).text($("#name_edit_".concat(itemId)).val());
    $("#type_".concat(itemId)).text($("#type_edit_".concat(itemId)).val());
    $("#cost_".concat(itemId)).text($("#cost_edit_".concat(itemId)).val());
    //hide the edit cols
    $("#name_edit_".concat(itemId)).hide()
    $("#type_edit_".concat(itemId)).hide()
    $("#cost_edit_".concat(itemId)).hide()
    $("#buttons_edit_".concat(itemId)).hide()
    //show the display cols
    $("#name_".concat(itemId)).show()
    $("#type_".concat(itemId)).show()
    $("#cost_".concat(itemId)).show()
    $("#buttons_".concat(itemId)).show()
}
function replaceAllSubsting (str, oldSubStr, newSubStr) {
    return str.split(oldSubStr).join(newSubStr);
}

function notesAjax(){
    messageDivId = "#message";
    typeDivId = "#note";
    arrivalDivId = "#arrival";
    assigneeDivId = "#assignee";
    departureDivId = "#departure";
    peopleOnsiteDivId = "#peopleOnSite";
    
    alert("notesAjax called still works");
    //validate the form
    if ($(messageDivId).val() != "") {
        postData = {}
        postData.job_id = $("#jobId").text()
        postData.apiKey = $("#apiKey").text()
        postData.tbl = $(typeDivId).val()
        postData.content = $(messageDivId).val()
        postData.arrival_time = $(arrivalDivId).val()
        postData.departure_time = $(departureDivId).val()
        postData.people_on_site = $(properlyeopleOnsiteDivId).val()
    }
    if($(messageDivId).val() != ""){
        $.ajax({
            url : "/forward/note",
            dataType:"text",
            method:"POST",
            data: JSON.stringify(postData),
            success:function(response){
              if (/^\d+$/.test(response)) {
                console.log("Successful add")
                //respone was only integers, adding was successful
              } else{
                console.log("Unsuccessful add")
                console.log(data)
                //response contained non numerics. Something bad happened
                $("#apiResponse").html(data)
              };
              
            }
        }); 
    }
    else{
        //didn't validate. Tell user where they goofed
        if ($(".message").val() == "") {
            flashRedBackground($(".message"));
        };  
        if($("#assignee") == ""){
            flashRedBackground($("#assignee"))
        };
        if($("#arrival") == ""){
            flashRedBackground($("#arrival"))
        };
        if($("#departure") == ""){
            flashRedBackground($("#departure"))
        };
        if($("#peopleOnSite") == ""){
            flashRedBackground($("#peopleOnSite"))
        };
    }; 
           
       
}