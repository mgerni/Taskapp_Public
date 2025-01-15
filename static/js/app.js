
//Email verification modal

// $(document).ready(function() {
//     $(document).on('click', '.emailButton', function() {
//         var valid = this.form.checkValidity();
//         $("#email").html(valid)
//         if (valid){


//             $('form').submit(false);
//             var email = $('#email').val();

//             req = $.ajax({
//                 url : '/email_verify/',
//                 type : 'POST',
//                 data : {email : email}
//             });

//             req.done(function(data)
//             {

//                 $('#emailverificationModal').html(data);
//             });
//         }
//     });
// });


//email verification modal?
// $(document).ready(function() {
//     $(document).on('click', '.emailButton2', function() {


//             $('form').submit(false);
//             var email = $('#email').val();


//             req = $.ajax({
//                 url : '/email_verify/',
//                 type : 'POST',
//                 data : {email : email}
//             });

//             req.done(function(data)
//             {

//                 $('#emailverificationModal').html(data);
//             });
        
//     });
// });

//Change Official status Modal button

// $(document).ready(function(){
//     $(document).on('click', '.changeOfficialButton', function(){
//         var official_status = false
//         req = $.ajax({
//             url : '/profile_change_official/',
//             type : 'POST',
//             data : {official_status : official_status}
//         });

//         req.done(function()
//         {
//             $('#changeOfficalStatusModal').modal('hide');
//             window.location.reload();
//         });

        
//     })
// });




// Changes input html for email change function.
// $(document).ready(function() {
//     $(document).on('click', '.emailChange', function() {


//             $('form').submit(false);
            
//             req = $.ajax({
//                 url : '/profile_emailChange/',
//                 type : 'POST'
                
//             });

//             req.done(function(data)
//             {
//                 $('#changeEmail').html(data);
//             });
        
//     });
// });


// Sends AJAX request to backend to change the email address. 
$(document).ready(function() {
    $(document).on('click', '.changeEmailSubmit', function() {
        var valid = this.form.checkValidity();
        $("#emailLabel").html(valid)
        if (valid){


            $('form').submit(false);
            var email = $('#emailLabel').val();
            req = $.ajax({
                url : '/profile_emailChangeSubmit/',
                type : 'POST',
                data : {email : email}
            });

            req.done(function(data)
            {

                $('#emailLabel').fadeOut(1000).fadeIn(1000);
                $('#changeEmail').html(data);
            });
        }
    });
});


//Changes input html for username change function.
$(document).ready(function() {
    $(document).on('click', '.usernameChange', function() {
            $('form').submit(false);
            req = $.ajax({
                url : '/profile_usernameChange/',
                type : 'POST'
            });
            req.done(function(data)
            {
                $('#changeEmail').html(data);
            });
        
    });
});



// Sends AJAX request to backend to change the username. 
$(document).ready(function() {
    $(document).on('click', '.changeUsernameSubmit', function() {
        $('form').submit(false);
        var username = $('#usernameLabel').val();
        console.log(username)
        req = $.ajax({
            url : '/profile_usernameChangeSubmit/',
            type : 'POST',
            data : {username : username}
        });

        req.done(function(data)
        {

            $('#usernameLabel').fadeOut(1000).fadeIn(1000);
            $('#changeEmail').html(data);
        });
    });
});

//Change Password Modal button
$(document).ready(function(){
    $(document).on('click', '.changePasswordButton', function(){
        $('form').submit(false);
        var change_password = $('#passwordChange').val();
        var confirm_password = $('#passwordChangeConfirm').val();
        req = $.ajax({
            url : '/profile_passwordChangeSubmit/',
            type : 'POST',
            data : {change_password : change_password, 
                    confirm_password: confirm_password}
        
        });
        req.done(function(data)
        {
            $('#error').html(data);
        });
    });
});






//Sends AJAX request on changed form-switch state for LMS status change function. 
$(document).ready(function() {
    
    $('#changeLMS').on('change.bootstrapSwitch', function(e) {
        var lms_status = e.target.checked
        if (lms_status == false) {
            req = $.ajax({
                url : '/change_lms_status/',
                type : 'POST',
                data : {lms_status : lms_status}
            });
        }
            
    });
});

//Sends AJAX request on changed form-switch state for LMS status change function.
$(document).ready(function() {
    
    $('#changeLMS').on('change.bootstrapSwitch', function(e) {
        var lms_status = e.target.checked
        if (lms_status == true) {
            req = $.ajax({
                url : '/change_lms_status/',
                type : 'POST',
                data : {lms_status : lms_status}
            });
        }
            
    });
});


//Provide Tip and URL data for taskHelpModal per task. 
$(document).ready(function(){
    $(document).on('click', '.taskHelpModal', function(){
        var tip = $(this).attr('tip');
        var link = $(this).attr('link')
        req = $.ajax({
            url : '/task_help/',
            type : 'POST',
            data : {tip: tip, link : link}
        });

        req.done(function(data)
        {
            $('#taskHelpModalBody').html(data);
            $('#taskHelpModal').modal('show');
        });
    });
});

$(document).on('click', '.collectionlogChecker', function(){
    $('form').submit(false);
    var username = $('#usernameVal').val();
    req = $.ajax({
        url : '/collectionlog_check/',
        type: 'POST',
        data : {username : username} 
    });

        req.done(function(data)
    {
        $('#modal_export_body').html(data);
        // $('#modal_export_footer').html('<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>');
    });
});

//Export Task App Progress to Google Sheets
//DISABLED DUE TO AUTOMATED COLLECTION LOG CHECKER
// $(document).ready(function(){
//     $(document).on('click', '.export_progress', function(){
//         //Change element #modal_export_body to Hold right while we export to google sheets.
//         // $('#modal_export_footer').html('<div class="text-center"><img src="/static/loading.gif" alt="Loading..." width="40" height="40"></div>');
//         $('#modal_export_footer').html('<img src="/static/loading.gif" alt="Loading..." width="40" height="40" class="me-5"><p class="text-white me-5">Exporting Progress...</p>');
//         // '<img src="/static/loading.gif" alt="Loading..." width="40" height="40"><p>Hold Tight while we export to Google Sheets!</p>'
//         // <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
//         // <button type="submit" class="btn btn-success export_progress">Export</button>

//         req = $.ajax({
//             url : '/export_progress/',
//             type : 'POST'
//         });

//         req.done(function(data)
//         {
//             $('#modal_export_body').html(data);
//             $('#modal_export_footer').html('<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>');
//         });
//     });
// });


$(document).ready(function(){
    $(document).on('click', '.topButton', function(){
        var myDiv = document.getElementById('tasklist');
        myDiv.scrollTop = 0;
    });
});



//Update TASK functions
$(document).ready(function() {

    $(document).on('click', '.updateButton', function() {

        var task_id = $(this).attr('task_id');
        var name = $(this).attr('name');
        if (name == 'easyTasks'){
            var task_type = 'task' + task_id + '_easy';
            var task_status = 'completed-task-easy';
        }
        else if (name == 'mediumTasks'){
            var task_type = 'task' + task_id + '_medium';
            var task_status = 'completed-task-medium';
        }
        else if (name == 'hardTasks'){
            var task_type = 'task' + task_id + '_hard';
            var task_status = 'completed-task-hard';
        }
        else if (name == 'eliteTasks'){
            var task_type = 'task' + task_id + '_elite';
            var task_status = 'completed-task-elite';
        }
        else if (name == 'passiveTasks'){
            var task_type = 'task' + task_id + '_passive';
            var task_status = 'completed-task-passive';
        }
        else if (name == 'extraTasks'){
            var task_type = 'task' + task_id + '_extra';
            var task_status = 'completed-task-extra';
        }
        else if (name == 'bossPetTasks'){
            var task_type = 'task' + task_id + '_bosspet';
            var task_status = 'completed-task-pets';
        }
        else if (name == 'skillPetTasks'){
            var task_type = 'task' + task_id + '_skillpet';
            var task_status = 'completed-task-pets';
        }
        else if (name == 'otherPetTasks'){
            var task_type = 'task' + task_id + '_otherpet';
            var task_status = 'completed-task-pets';
        }
        var eleTarget = document.getElementsByClassName(task_type)[0];

        req = $.ajax({
            url : '/update_completed/',
            type : 'POST',
            data : {id : task_id, name : name}

        });
        req.done(function(data)
        {
            $(eleTarget).fadeOut(1000).fadeIn(1000);
            $(eleTarget).addClass('bg-success')
            $(eleTarget).id = task_status
            $(eleTarget).html(data)
            document.getElementsByClassName(task_type)[0].id = task_status;
            
        });
    });

});

//Revert TASK functions 
$(document).ready(function() {

    $(document).on('click', '.revertButton', function() {

        var task_id = $(this).attr('task_id');
        var name = $(this).attr('name');
        if (name == 'easyTasks'){
            var task_type = 'task' + task_id + '_easy';
            var task_status = 'incomplete-task-easy';
        }
        else if (name == 'mediumTasks'){
            var task_type = 'task' + task_id + '_medium';
            var task_status = 'incomplete-task-medium';
        }
        else if (name == 'hardTasks'){
            var task_type = 'task' + task_id + '_hard';
            var task_status = 'incomplete-task-hard';
        }
        else if (name == 'eliteTasks'){
            var task_type = 'task' + task_id + '_elite';
            var task_status = 'incomplete-task-elite';
        }
        else if (name == 'passiveTasks'){
            var task_type = 'task' + task_id + '_passive';
            var task_status = 'incomplete-task-passive';
        }
        else if (name == 'extraTasks'){
            var task_type = 'task' + task_id + '_extra';
            var task_status = 'incomplete-task-extra';
        }
        else if (name == 'bossPetTasks'){
            var task_type = 'task' + task_id + '_bosspet';
            var task_status = 'incomplete-task-pets';
        }
        else if (name == 'skillPetTasks'){
            var task_type = 'task' + task_id + '_skillpet';
            var task_status = 'incomplete-task-pets';
        }
        else if (name == 'otherPetTasks'){
            var task_type = 'task' + task_id + '_otherpet';
            var task_status = 'incomplete-task-pets';
        }
        var eleTarget = document.getElementsByClassName(task_type)[0];

        req = $.ajax({
            url : '/revert_completed/',
            type : 'POST',
            data : {id : task_id, name : name}

        });
        req.done(function(data)
        {
            $(eleTarget).fadeOut(1000).fadeIn(1000);
            $(eleTarget).removeClass('bg-success')
            $(eleTarget).id = task_status
            $(eleTarget).html(data)
            document.getElementsByClassName(task_type)[0].id = task_status;
            
        });



    });

});


  $(document).ready(function() {
    $(document).on("click", "#questList", function(event) {
      var modal = document.getElementById("questModal");
      modal.style.display = "block";
    });
  });

  $(document).ready(function(){
    $(document).on("click", "#questModalClose", function(){
        var modal = document.getElementById("questModal");
        modal.style.display = "none";
    });
  });


  $(document).ready(function() {
    $(document).on("click", "#farmModalOpen", function(event) {
      var modal = document.getElementById("farmModal");
      modal.style.display = "block";
    });
  });



  $(document).ready(function(){
    $(document).on("click", "#farmModalClose", function(){
        var modal = document.getElementById("farmModal");
        modal.style.display = "none";
    });
  });


  $(document).ready(function() {
    $(document).on("click", "#ancientPageModalOpen", function(event) {
      var modal = document.getElementById("ancientPageModal");
      modal.style.display = "block";
    });
  });


  $(document).ready(function(){
    $(document).on("click", "#ancientPageModalClose", function(){
        var modal = document.getElementById("ancientPageModal");
        modal.style.display = "none";
    });
  });
