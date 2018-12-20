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
	$("#slider-photo").owlCarousel({
		margin:10,
		responsiveClass:true,
		responsive:{
			0:{
				items:1,
				nav:true
			},
			600:{
				items:3,
				nav:true
			},
			1000:{
				items:3,
				nav:true,
				loop:false
			}
		},

		navText: [
			'<span aria-label="' + 'Previous' + '">&larr;</span>',
			'<span aria-label="' + 'Next' + '">&rarr;</span>'
		],
		// autoPlay:true,
		nav:true,
		autoHeight: true,
		dots:false
	});

	$("#slider-text").owlCarousel({
		margin:40,
		responsiveClass:true,
		responsive:{
			0:{
				items:1,
				nav:true
			},
			600:{
				margin:20,
				items:3,
				nav:true
			},
			1200:{
				items:4,
				nav:true,
				loop:false
			}
		},

		navText: [
			'<span aria-label="' + 'Previous' + '">&larr;</span>',
			'<span aria-label="' + 'Next' + '">&rarr;</span>'
		],
		// autoPlay:true,
		nav:true,
		// autoHeight: true,
		dots:false
	});
});


