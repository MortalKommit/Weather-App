$(document).ready(function () {

  $('form[name="add_city"]').on('submit', function (event) {

    req = $.ajax({
      data: {
        city_name: $('#input-city').val()
      },
      type: 'POST',
      url: '/add',
      timeout: 20000,
      success: function (response) {
        console.log(response);
        $('.cards').html(response)
      },
      error: function (error) {
        console.log(error);
      }
    });

    event.preventDefault();
  });
});
