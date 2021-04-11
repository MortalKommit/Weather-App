$(document).ready(function () {

  $('form[name="add_city"]').on('submit', function (event) {

    req = $.ajax({
      data: {
        city_name: $('#input-city').val()
      },
      type: 'POST',
      url: '/add',
      timeout: 20000,
      error: function (error) {
        console.log(error);
      }
    })

    req.done(function (response) {
      $('.cards').html(response);
    });
    event.preventDefault();
  });

  $('form[name="del_city"]').on('submit', function (event) {
    del_req = $.ajax({
      type: 'POST',
      url: $(this).closest('form').attr('action'),
      timeout: 20000,
      error: function (error) {
        console.log(error);
      }
    });
    del_req.done(function (response) {
      console.log(response);
    });
    event.preventDefault();
  });
});
