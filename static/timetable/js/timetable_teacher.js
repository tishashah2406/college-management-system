(function($) {

    $(document).ready(function() {

        console.log("Timetable JS loaded");


        $("#id_course").change(function() {

            let courseId = $(this).val();

            let teacher = $("#id_teacher");


            if (!courseId) {
                teacher.val("");
                return;
            }


            $.ajax({

                url: "/admin/timetable/timetable/get-teachers/",

                data: {
                    course: courseId
                },


                success: function(data) {

                    console.log("Teachers:", data);


                    teacher.empty();


                    if (data.length === 1) {

                        // automatically select only teacher
                        teacher.append(
                            $("<option>", {
                                value: data[0].id,
                                text: data[0].name
                            })
                        );


                        teacher.val(data[0].id).trigger("change");


                    } else {


                        teacher.append(
                            $("<option>", {
                                value:"",
                                text:"---------"
                            })
                        );


                        $.each(data, function(index, item) {

                            teacher.append(
                                $("<option>", {
                                    value:item.id,
                                    text:item.name
                                })
                            );

                        });

                    }

                },


                error:function(xhr){

                    console.log(xhr.responseText);

                }


            });


        });


    });


})(django.jQuery);