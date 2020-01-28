//Включение всплывающих подсказок
$(function () {
	$('[data-toggle="popover"]').popover();
	$('[data-toggle="tooltip"]').tooltip();
})

// Кнопка - Наверх
$(document).ready(function() {
	$('body').append('<button class="top-arrow">');
	$('.top-arrow').click(function() {
		$('body').animate({'scrollTop': 0}, 1000);
		$('html').animate({'scrollTop': 0}, 1000);
	});
	$(window).scroll(function(){
		if ($(window).scrollTop() > 300) {
			$(".top-arrow").addClass("top-arrow-active");
		}
		else {
			$(".top-arrow").removeClass("top-arrow-active");
		}
	});
});

// Slider
$(document).ready(function() {
	// $("#slider-photo").owlCarousel({
	// 	margin:10,
	// 	responsiveClass:true,
	// 	responsive:{
	// 		0:{
	// 			items:1,
	// 			nav:true
	// 		},
	// 		600:{
	// 			items:3,
	// 			nav:true
	// 		},
	// 		1000:{
	// 			items:3,
	// 			nav:true,
	// 			loop:false
	// 		}
	// 	},

	// 	navText: [
	// 		'<span aria-label="' + 'Previous' + '">&larr;</span>',
	// 		'<span aria-label="' + 'Next' + '">&rarr;</span>'
	// 	],
	// 	// autoPlay:true,
	// 	nav:true,
	// 	autoHeight: true,
	// 	dots:false
	// });

	// $("#slider-text").owlCarousel({
	// 	margin:40,
	// 	responsiveClass:true,
	// 	responsive:{
	// 		0:{
	// 			items:1,
	// 			nav:true
	// 		},
	// 		600:{
	// 			margin:20,
	// 			items:3,
	// 			nav:true
	// 		},
	// 		1200:{
	// 			items:4,
	// 			nav:true,
	// 			loop:false
	// 		}
	// 	},

	// 	navText: [
	// 		'<span aria-label="' + 'Previous' + '">&larr;</span>',
	// 		'<span aria-label="' + 'Next' + '">&rarr;</span>'
	// 	],
	// 	// autoPlay:true,
	// 	nav:true,
	// 	// autoHeight: true,
	// 	dots:false
	// });
	$('#toggle_panel').click(function(event){
		event.preventDefault();
		$('.admin_panel').toggle();
		if ($('.admin_panel').is(":visible")) {
		  $('#toggle_panel').html('<i class="fas fa-arrow-up"></i>');
		} else {
		  $('#toggle_panel').html('<i class="fas fa-arrow-down"></i>');
		}
	  });

	$('#order_service_button').click(function(event) {
		event.preventDefault();
		console.log('order clicked');

		order = $('#order_form').serializeArray();
		// console.table(order);
		console.log(order)
		$.post('/accept_order/', order)
		  .done(response=>{
			  if (response['order_id']) {
				var id = response['order_id'];
				$('.modal-title:visible').text('Спасибо!');
				$('.modal-header > .row:visible').hide();
				$('.modal-body:visible').html(`
				<h3 class="text text-white">
				  Обращение зарегистрировано, идентификатор заявки ${id}
				</h3>
				<p class="text text-white py-3">
				  В ближайшее время с Вами свяжется наш специалист
				</p>
				`);
				$('.modal-footer:visible').hide();
			  }

			  if (response['errors']) {
				$('.invalid-feedback').remove();
				$('.border').each(function() {
				  $(this).removeClass('border border-danger');
				});
				for (let key in response['errors']) {
				  // remove all red borders
				  // $('.border-danger').removeClass('is-invalid border border-danger');
				  // $('.invalid-feedback:visible').hide();
				  console.log(
					key, ":", response['errors'][key]
					);
				  let form = $("#order_form");
				  let element = form.find(`input[name="${key}"]`);

				  // element.after(`<small class="text-danger">${response['errors'][key]}</small>`);
				  element.addClass('is-invalid border border-danger');
				  element.after(`<div class="invalid-feedback">${response['errors'][key]}</div>`);
				  if (key == 'captcha') {
					let captcha_div = $('#order_captcha_check');
					captcha_div.addClass('border border-danger');
					captcha_div.css("border-radius", "3px");
					$('#order_captcha_message').html(
					`<p class="text text-danger">
					  ${response['errors'][key]}
					</p>`
					)}
				}
			  }
			}
		  )
		  .fail(response=>{
			console.log('fail', response);
			console.log(response);
			}
		  );
	  });
});


