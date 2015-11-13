var imgData;

//**************************Start Photos stuff********************************************************************************************
function photosInit() {
    //things that have to the first time the page loads
    prepPhotos()
    $('#img-loader').hide()
    $("a.gallery").fancybox({
        'transitionIn'  :   'elastic',
        'transitionOut' :   'elastic',
        'speedIn'       :   600, 
        'speedOut'      :   200, 
        'overlayShow'   :   false,
        'cyclic'        :   true,
        'showNavArrows' :   true
    });
    $("#show-photos").hide();
    $("#show-photos").click(function(){
        $("#show-photos").hide();
        $("#hide-photos").show();
        $("#photos-container").slideDown("slow");   
    });
    $("#hide-photos").click(function(){
        $("#hide-photos").hide();
        $("#show-photos").show();
        $("#photos-container").slideUp("slow");   
    });
}
function prepPhotos() {
    //things that have to happen every time a new photo is added
    document.getElementById('img-file').onchange = function (e) {loadFileFromInput(e.target);};
    $('#cancelImage').click(function(){
        imgData = {}
        $('#img-preview').removeAttr("src");
        $('#img-preview-container').hide();
        $("#img-file").replaceWith($("#img-file").clone());
        document.getElementById('img-file').onchange = function (e) {loadFileFromInput(e.target);};
    });
    $('#submitImage').click(function(){
        $('#img-loader').show()
        $("#img-loader").width($("#img-preview").width());
        $.post("/forward/photo", JSON.stringify(imgData))
            .done(
                function(response) {
                    $('#img-loader').hide()
                    console.log("response: " + response)
                    if (apiResponseIsGood(response)) {
                        createNewPhoto(imgData);
                    };
                }
            );
    });
    $('#img-preview-container').hide()
}
function loadFileFromInput(input) {
    var reader; 
    if (input.files && input.files[0]) {
        var file = input.files[0];
        reader = new FileReader();
        reader.readAsDataURL(file);
        //filereaders run on a different thread, so we
        // need to wait for it to finish it's work before we continue
        reader.onload = function (e) {
            imgData = {}
            imgData.name = file.name
            imgData.lastModified = file.lastModified
            imgData.type = file.type
            imgData.file_extension = (file.name).substr((file.name).lastIndexOf('.'))
            imgData.job_id = $('#jobId').text()
            imgData.base64_image = reader.result
            console.log(imgData)
            $('#img-preview').attr("src",reader.result);
            $('#img-preview-container').show()
        }
    }
}
function createNewPhoto(photo){
    console.log("new photo")
    newNote = $("#image-template").html()
    newNote = replaceAllSubsting(newNote, "!url!", photo.base64_image);
    newNote = replaceAllSubsting(newNote, "!gallery!", "gallery01");
    $('#gallery > div:last-child').after(newNote);
    $("#add-image-card").replaceWith($("#add-image-card").clone());
    prepPhotos();
}

//**************************End Photos stuff********************************************************************************************



function prepNotes() {
    $(".daily-report-field").hide()
    $(".action-item-field").hide()
    $(".date-time-error").hide();
    $(".note-edit").hide()
    $("#show-notes").hide();
    $("#show-notes").click(function(){
        $("#show-notes").hide();
        $("#hide-notes").show();
        $("#notes-container").slideDown("slow");   
    });
    $("#hide-notes").click(function(){
        $("#hide-notes").hide();
        $("#show-notes").show();
        $("#notes-container").slideUp("slow");   
    });
    $(".add-note-card").removeClass("card-warning card-danger").addClass("card-info");
    $('.note-card').width($('#add-note-card').width())
    $('.note-add-assignee').click(function(){
        buttonId = $(this).attr('id').split("-")
        noteId = buttonId[buttonId.length -1]
        noteTbl = buttonId[buttonId.length -2]
        $("#note-assigned-name-"+noteTbl+"-"+noteId).hide()
        $("#note-add-assignee-"+noteTbl+"-"+noteId).hide()
        $("#note-select-assignee-"+noteTbl+"-"+noteId).show()
        $("#note-save-assignee-"+noteTbl+"-"+noteId).show()
        $("#note-cancel-assignee-"+noteTbl+"-"+noteId).show()
        makeUsersDropdown("all", "#note-select-assignee-"+noteTbl+"-"+noteId)
    });
    $('.note-cancel-assignee').click(function(){
        buttonId = $(this).attr('id').split("-")
        noteId = buttonId[buttonId.length -1]
        noteTbl = buttonId[buttonId.length -2]
        $("#note-assigned-name-"+noteTbl+"-"+noteId).show()
        $("#note-add-assignee-"+noteTbl+"-"+noteId).show()
        $("#note-select-assignee-"+noteTbl+"-"+noteId).hide()
        $("#note-save-assignee-"+noteTbl+"-"+noteId).hide()
        $("#note-cancel-assignee-"+noteTbl+"-"+noteId).hide()
        $("#note-select-assignee-"+noteTbl+"-"+noteId).html("")
    });
    $('.note-save-assignee').click(function(){
        buttonId = $(this).attr('id').split("-")
        noteId = buttonId[buttonId.length -1]
        noteTbl = buttonId[buttonId.length -2]
        var noteId = noteId
        if ($("#note-select-assignee-"+noteTbl+"-"+noteId).val() >= 0){
            postData = {}
            postData.id = noteId
            postData.assigned_user = $("#note-select-assignee-"+noteTbl+"-"+noteId).val() 
            $.ajax({
                url : "/forward/actionItem",
                dataType:"text",
                method:"POST",
                data: JSON.stringify(postData),
                success:function(response){
                    if (apiResponseIsGood(response)) {
                        console.log("Successful update")
                        console.log(postData)
                        console.log(response)
                        assignee = jQuery.parseJSON(response);
                        newAssignee = $("#assigned-user-template").html()
                        newAssignee = replaceAllSubsting(newAssignee, "!email!", assignee.email);
                        newAssignee = replaceAllSubsting(newAssignee, "!phone!", assignee.phone);
                        newAssignee = replaceAllSubsting(newAssignee, "!name!", assignee.name);
                        newAssignee = replaceAllSubsting(newAssignee, "!id!", noteId);
                        $("#note-assignee-actionItems-"+noteId).html(newAssignee)
                        prepNotes();
                    } else {
                        console.log("Unsuccessful delete")
                        $("#apiResponse").html(response)
                    };
                }
            })
        }
        else{
            flashRedBackground($("#note-select-assignee-"+noteTbl+"-"+noteId))
        };
    });
    makeUsersDropdown("all", "#note-assignee-select")
}
function prepBudget(){
    $(".addItemForm").hide();
    $(".edit_row").hide();
    $("#show-budget").hide();
    $("#show-budget").click(function(){
        $("#show-budget").hide();
        $("#hide-budget").show();
        $("#budget-table-div").slideDown("slow");   
    });
    $("#hide-budget").click(function(){
        $("#hide-budget").hide();
        $("#show-budget").show();
        $("#budget-table-div").slideUp("slow");   
    });
    $("#cancelBudgetAdd").click(function(){
        $("#name").val("");
        $("#type").val("select");
        $("#cost").val("");
        $(".addItemForm").hide()
        $("#showBudgetAdd").show()
    });
    $("#showBudgetAdd").click(function(){
        $(".addItemForm").show()
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
    $("[id^=save_]").click(function(){
        buttonId = $(this).attr('id').split("_")
        itemId = buttonId[buttonId.length -1]
        budgetItemAjax(itemId)
    });
    $("[id^=delete_]").click(function(){
        buttonId = $(this).attr('id').split("_")
        itemId = buttonId[buttonId.length -1]
        postData = {}
        postData.id = itemId
        $.ajax({
            url : "/forward/delete/budgetItem",
            dataType:"text",
            method:"POST",
            data: JSON.stringify(postData),
            success:function(response){
                if (apiResponseIsGood(response)) {
                    console.log("Successful delete")
                    console.log(postData)
                    console.log(response)
                    $("#item_".concat(itemId)).remove()
                } else {
                    console.log("Unsuccessful delete")
                    $("#apiResponse").html(response)
                };
            }
        });
    });
}
function flashRedBackground (div) {
    bg = div.css("background");
    div.css("background", "red");
    setTimeout(function(){
        div.css("background", bg);
    }, 2000);
}
function selectedNote(){
    $(".daily-report-field").hide()
    $(".action-item-field").hide()
    $(".add-note-card").removeClass("card-warning card-danger").addClass("card-info");
}
function selectedDailyReport(){
    $(".daily-report-field").show()
    $(".action-item-field").hide()
    $(".add-note-card").removeClass("card-info card-danger").addClass("card-warning");
}
function selectedActionItem(){
    $(".daily-report-field").hide()
    $(".action-item-field").show()
    $(".add-note-card").removeClass("card-info card-warning").addClass("card-danger");
}
function budgetItemAjax(itemId){
    nameDivId = "#name";
    typeDivId = "#type";
    costDivId = "#cost";
    if (itemId != null){
        nameDivId = nameDivId.concat("_edit_"+itemId);
        typeDivId = typeDivId.concat("_edit_"+itemId);
        costDivId = costDivId.concat("_edit_"+itemId);
    };
    //validate the form
    if ($(nameDivId).val() != "" && $(typeDivId).val() != "select" && $(typeDivId).val() != "" && $(costDivId).val() != "") {
        postData = {}
        if (itemId != null){
            postData.id = itemId
        }
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
              if (apiResponseIsGood(response)) {
                console.log("Successful add")
                //respone was only integers, adding was successful
                if (itemId != null){
                    //we're editing
                    updateBudgetItemRow(itemId)
                }
                else{
                    //we're adding
                    newBudgetItemRow(response);
                };
              } else{
                console.log("Unsuccessful add")
                console.log(response)
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
        if ($(typeDivId).val() == "select" || $(typeDivId).val() != "") {
            flashRedBackground($(typeDivId));
        };
        if ($(costDivId).val() == "") {
            flashRedBackground($(costDivId));
        };
    };        
}
function makeUsersDropdown(type, selectId){
    var selectId = selectId;
    $.get( "/forward/users/type/"+type, function(data){
        var data = jQuery.parseJSON(data);
        data.forEach(function(obj) {
            option = "<option value=\""+obj.id+"\">"+obj.name+"</option>";
            $(selectId).append(option);
        });
        option = "<option value=\"-1\">Select</option>";
        $(selectId).prepend(option);
    });
}
function newBudgetItemRow(itemId){
    //create new row from template
    rowTemplate = $("#budgetRowTemplate").html()
    newRow = replaceAllSubsting(rowTemplate, "!template!", itemId);
    $('#budget-table tr:last').before(newRow);
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
function apiResponseIsGood(response){
    pattStr1 = "^2\\d\\d.*"
    pattStr2 = "^[0-9]*$"
    pattStr3 = "^\\{.*$"
    var pattern1 = new RegExp(pattStr1)
    var pattern2 = new RegExp(pattStr2)
    test1 = pattern1.test(response)
    test2 = pattern2.test(response)
    result = test1 || test2 || (response.charAt(0) == "{")
    if(!result){
        console.log(test1)
        console.log(test2)
        console.log(test3)
    }
    console.log(result)
    return result
}
function notesAjax(){
    messageDivId = "#note-message";
    assigneeDivId = "#note-assignee";
    arrivalDivId = "#note-arrivalTime";
    departureDivId = "#note-departureTime";
    peopleOnsiteDivId = "#note-PeopleOnSite";
    
    //alert("notesAjax called still works");
    //validate the form
    if (($("#note-type-dailyReport").prop("checked") == false &&
            ($(messageDivId).val() != "")) ||
        ($("#note-type-dailyReport").prop("checked") == true &&
            ($(messageDivId).val() != "") &&
            ($(arrivalDivId).val() != "") &&
            ($(departureDivId).val() != ""))
        ) {
        postData = {}
        if($("#note-type-actionItem").prop("checked") == true){

            postData.assignee = $(assigneeDivId).val();
            postData.tbl = "actionItems"
        }
        else if($("#note-type-dailyReport").prop("checked") == true){
            if($(arrivalDivId).val() != "" && $(departureDivId).val() != ""){
                postData.arrival_time = $(arrivalDivId).val()
                postData.departure_time = $(departureDivId).val()
                postData.people_on_site = $(peopleOnsiteDivId).val()
                postData.tbl = "dailyReports"
            }
        }
        else{
            postData.tbl = "notes"
        }
        postData.job_id = $("#jobId").text()
        postData.contents = $(messageDivId).val()

        $.ajax({
            url : "/forward/note",
            dataType:"text",
            method:"POST",
            data: JSON.stringify(postData),
            success:function(response){
              if (apiResponseIsGood(response)) {
                console.log("Successful add")
                console.log(JSON.stringify(postData))
                console.log(response)
                createNewNote(response, postData);
              } else{
                console.log("Unsuccessful add")
                console.log(JSON.stringify(postData))
                console.log(response)
                $("#apiResponse").html(response)
              };
              
            }
        }); 
    }
    else{
        console.log("Note didn't validate")
        if($("#note-arrivalTime").val() == ""){
            flashRedBackground($("#note-arrivalTime"))
        };
        if($("#note-departureTime").val() == ""){
            flashRedBackground($("#note-departureTime"))
        };
        if($("#note-message").val() == ""){
            flashRedBackground($("#note-message"))
        };
    }
    
}  
function createNewNote(noteId, note){
    console.log("new note")
    noteSuffix = "-" + note.tbl + "-" + noteId
    console.log(note)
    console.log(note.contents)
    console.log(note.tbl)
    newNote = $("#"+note.tbl+"-template").html()
    newNote = replaceAllSubsting(newNote, "!tbl!", note.tbl);
    newNote = replaceAllSubsting(newNote, "!id!", noteId);

    $('#note-card-group > div:first-child').before(newNote);

    $("#note-contents".concat(noteSuffix)).text(note.contents)
    $("#note-user-name".concat(noteSuffix)).text($("#user-name").text())
    d = new Date()
    date = d.getFullYear()+"-"+(d.getMonth()+1)+"-"+d.getDate()
    time = " "+d.getHours()+":"+d.getMinutes()+":"+d.getSeconds()
    datetime = date+time
    $("#note-entry-time".concat(noteSuffix)).text(datetime)

    if (note.tbl == "actionItems") {
        if (note.assignee != "") {
            $("#note-assigned-name".concat(noteSuffix)).text(note.assignee)
            $("#note-add-assignee".concat(noteSuffix)).hide()
        } else{
            $("#note-assigned-name".concat(noteSuffix)).hide()
        };
    }else if (note.tbl == "dailyReports") {
        $("#note-arrival".concat(noteSuffix)).text(date+" "+note.arrival_time)
        $("#note-departure".concat(noteSuffix)).text(date+" "+note.departure_time)
        $("#note-people".concat(noteSuffix)).text(note.people_on_site)
    };
    //empty the form
    $("#note-message").val("")
    $("#note-assignee").val("")
    $("#note-arrivalTime").val("")
    $("#note-departureTime").val("")
    $("#note-PeopleOnSite").val("")
    //make all notes the same size
    $('.note-card').width($('.add-note-card').width())
    prepNotes();
}
//dynamic text area for the job name and job description
//hides all the fields with the job-edit id
function jobEditInit(){
	$(".job-edit").hide();
	
	//function to show hidden stuff when ' (edit)' clicked
	$("#edit-job").click(function(){
        $(".job-show").hide();
		$(".job-edit").show();  
    });
	
	/*$(function(){
		$("#edit-job-desc").redactor({
			focus: true,
			callbacks: {
				init: function(){
					this.code.set($('#job-desc').text());
				}
			}
		});
		
		$("#edit-job-name").redactor({
			focus: true,
			callbacks: {
				init: function(){
					this.code.set($('#job-name').text());
				}
			}
		});
	});*/
}
//changes the edit link to save link
/*$("#edit-job").click(function(){
		var container = $('#jobInfoTemplate');
		container.find('a#edit-job').unbind('click').click(SaveEditState).html(' (save)'); //this changes edit button to save button
		
});*/

$(document).ready(function(){
    photosInit()
    prepNotes()
    prepBudget()
	jobEditInit()
});
