/*
Theme Name: Mrittik Architecture Theme
Version: 1.0
Author: WPThemeBooster
Author URI: 
Description: Mrittik is a Modern Architecture Theme
*/
/*	IE 10 Fix*/

(function ($) {
	'use strict';
	
	jQuery(document).ready(function () {

        // Preloader
        setTimeout(function() {
            $('#preloader').addClass('hide');
        }, 1000);

        // Add Menu Item Current Class Auto
        function dynamicCurrentMenuClass(selector) {
          let FileName = window.location.href.split("/").reverse()[0];

          selector.find("li").each(function () {
            let anchor = $(this).find("a");
            if ($(anchor).attr("href") == FileName) {
              $(this).addClass("active");
            }
          });
          // if any li has .current elmnt add class
          selector.children("li").each(function () {
            if ($(this).find(".active").length) {
              $(this).addClass("active");
            }
          });
          // if no file name return
          if ("" == FileName) {
            selector.find("li").eq(0).addClass("active");
          }
        }
        
        if ($('.mainnav .main-menu').length) {
          dynamicCurrentMenuClass($('.mainnav .main-menu'));
		}

        // Mobile Responsive Menu 
        var mobileLogoContent = $('header .logo').html();
        var mobileMenuContent = $('.mainnav').html();
		$('.mr-menu .logo').append(mobileLogoContent);
		$('.mr-menu .mr_navmenu').append(mobileMenuContent);
        $( '.mr-menu .mr_navmenu ul.main-menu li.menu-item-has-children').append( $( "<span class='submenu_opener'><i class='bi bi-chevron-right'></i></span>" ) );

        // Sub-Menu Open On-Click
        $('.mr-menu ul.main-menu li.menu-item-has-children .submenu_opener').on("click", function(e){
            $(this).parent().toggleClass('nav_open');
            $(this).siblings('ul').slideToggle();
            e.stopPropagation();
            e.preventDefault();
        });
        
        // Active Mobile Responsive Menu : Add Class in body tag
        $('.mr-menu_toggle').on('click', function(e) {
            $('body').addClass('mr-menu_active');
            e.stopPropagation();
            e.preventDefault();
        });
        $('.mr-menu_close').on('click', function(e) {
            $('body').removeClass('mr-menu_active');
            e.stopPropagation();
            e.preventDefault();
        });
        $('.mr-menu_overlay').on('click', function(e) {
            $('body').removeClass('mr-menu_active');
            e.stopPropagation();
            e.preventDefault();
        });
    

        // Aside info bar
        $('.aside_open').on("click", function(e) {
            e.preventDefault();
            $('.aside_info_wrapper').addClass('show');
        });
        $('.aside_close').on("click", function(e) {
            e.preventDefault();
            $('.aside_info_wrapper').removeClass('show');
        });

        // Toggle Header Search
        $('.header_search .form-control-submit').on("click", function() {
            $('.open_search').toggleClass('active');
        });

        // Sticky Header
        var header = $("header");
        $(window).scroll(function() {
            var scroll = $(window).scrollTop();

            if (scroll >= 50) {
                header.addClass("sticky");
            } else {
                header.removeClass("sticky");
            }
        });

        // Partner Carousel 
        var Swiper1 = new Swiper('.wptb-partner--carousel .swiper-container', {
            loop: true,
            autoplay: {
                delay: 4000,
            },
            speed: 1500,
            slidesPerView: 1,
            spaceBetween: 0,
            breakpoints: {
                320: {
                  slidesPerView: 2,
                  spaceBetween: 20
                },
                480: {
                  slidesPerView: 3,
                  spaceBetween: 30
                },
                640: {
                  slidesPerView: 4,
                  spaceBetween: 30
                },
                768: {
                  slidesPerView: 5,
                  spaceBetween: 40
                },
                1200: {
                  slidesPerView: 6,
                  spaceBetween: 50
                }
            }
        });

        // Partner Carousel 
        var SwiperEmail = new Swiper('.wptb-partner--carousel.style-email .swiper-container', {
          loop: true,
          autoplay: {
              delay: 4000,
          },
          speed: 1500,
          slidesPerView: 1,
          spaceBetween: 0,
          breakpoints: {
              320: {
                slidesPerView: 2,
                spaceBetween: 20
              },
              480: {
                slidesPerView: 3,
                spaceBetween: 30
              },
              768: {
                slidesPerView: 4,
                spaceBetween: 40
              },
              1200: {
                slidesPerView: 5,
                spaceBetween: 50
              }
          }
        });

        // Partner Carousel 
        var SwiperEmail = new Swiper('.wptb-partner--carousel.style-ai .swiper-container', {
          loop: true,
          autoplay: {
              delay: 4000,
          },
          speed: 1500,
          slidesPerView: 1,
          spaceBetween: 0,
          breakpoints: {
              320: {
                slidesPerView: 2,
                spaceBetween: 20
              },
              480: {
                slidesPerView: 3,
                spaceBetween: 30
              },
              768: {
                slidesPerView: 4,
                spaceBetween: 40
              },
              1200: {
                slidesPerView: 5,
                spaceBetween: 50
              }
          }
        });

        // Partner Carousel 
        var SwiperStartup = new Swiper('.wptb-partner--carousel.style-startup .swiper-container', {
          loop: true,
          autoplay: {
              delay: 4000,
          },
          speed: 1500,
          slidesPerView: 1,
          spaceBetween: 0,
          breakpoints: {
              320: {
                slidesPerView: 2,
                spaceBetween: 20
              },
              480: {
                slidesPerView: 3,
                spaceBetween: 30
              },
              768: {
                slidesPerView: 4,
                spaceBetween: 40
              },
              1200: {
                slidesPerView: 5,
                spaceBetween: 50
              }
          }
        });

        // Service Carousel
        var ServicesCarousel1 = new Swiper('.wptb-services--carousel1 .swiper-container', {
            loop: true,
            // autoplay: {
            //     delay: 4000,
            // },
            speed: 1500,
            slidesPerView: 1,
            // centeredSlides: true,
            spaceBetween: 0,
            breakpoints: {
                320: {
                  slidesPerView: 1,
                  spaceBetween: 20
                },
                768: {
                  slidesPerView: 2,
                  spaceBetween: 40
                },
                1200: {
                  slidesPerView: 2,
                  spaceBetween: 50
                },
                1368: {
                  slidesPerView: 3,
                  spaceBetween: 50,
                  centeredSlides: true,
                }
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true
            },
        });

        // Service Carousel
        var ServicesCarousel2 = new Swiper('.wptb-services--carousel2 .swiper-container', {
            loop: true,
            // autoplay: {
            //     delay: 4000,
            // },
            speed: 1500,
            slidesPerView: 1,
            // centeredSlides: true,
            spaceBetween: 30,
            breakpoints: {
                320: {
                  slidesPerView: 1,
                },
                600: {
                  slidesPerView: 2,
                },
                1200: {
                  slidesPerView: 3,
                },
                1368: {
                  slidesPerView: 4,
                }
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true
            },
        });

        // Service Carousel
        var ServicesCarousel3 = new Swiper('.wptb-services--carousel3 .swiper-container', {
          loop: true,
          // autoplay: {
          //     delay: 4000,
          // },
          speed: 1500,
          slidesPerView: 1,
          // centeredSlides: true,
          spaceBetween: 6,
          breakpoints: {
              320: {
                slidesPerView: 1,
              },
              600: {
                slidesPerView: 2,
              },
              1200: {
                slidesPerView: 3,
              }
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
      });

        // Metabox Carousel
        var Swiper4 = new Swiper('.wptb-meta-box-carousel1 .swiper-container', {
            loop: true,
            // autoplay: {
            //     delay: 4000,
            // },
            speed: 1500,
            slidesPerView: 1,
            // centeredSlides: true,
            spaceBetween: 0,
            breakpoints: {
                320: {
                  slidesPerView: 1,
                  spaceBetween: 20
                },
                768: {
                  slidesPerView: 2,
                  spaceBetween: 20
                },
                1200: {
                  slidesPerView: 3,
                  spaceBetween: 20
                },
                1368: {
                  slidesPerView: 4,
                  spaceBetween: 20,
                  // centeredSlides: true,
                }
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true
            },
        });

        // Metabox Carousel
        var MetaboxStartup = new Swiper('.wptb-meta-box-carousel1.style-startup .swiper-container', {
          loop: true,
          // autoplay: {
          //     delay: 4000,
          // },
          speed: 1500,
          slidesPerView: 1,
          spaceBetween: 0,
          breakpoints: {
              320: {
                slidesPerView: 1,
                spaceBetween: 20
              },
              768: {
                slidesPerView: 2,
                spaceBetween: 20
              },
              1200: {
                slidesPerView: 4,
                spaceBetween: 20
              },
              1368: {
                slidesPerView: 4,
                spaceBetween: 20,
              }
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
      });

        // Testimonial Carousel
        var Swiper5 = new Swiper('.wptb-testimonial--carousel1 .swiper-container', {
            loop: true,
            // autoplay: {
            //     delay: 4000,
            // },
            speed: 1500,
            slidesPerView: 1,
            centeredSlides: true,
            spaceBetween: 30,
            breakpoints: {
                320: {
                  slidesPerView: 1,
                  spaceBetween: 20
                },
                768: {
                  slidesPerView: 2,
                },
                1200: {
                  slidesPerView: 2,
                },
                1368: {
                  slidesPerView: 2,
                }
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true
            },
        });

        // Testimonial Carousel
        var Swiper5_1 = new Swiper('.wptb-testimonial--carousel1.no-center .swiper-container', {
          loop: true,
          // autoplay: {
          //     delay: 4000,
          // },
          speed: 1500,
          slidesPerView: 1,
          centeredSlides: false,
          spaceBetween: 30,
          breakpoints: {
              320: {
                slidesPerView: 1,
                spaceBetween: 20
              },
              768: {
                slidesPerView: 1,
              },
              1200: {
                slidesPerView: 2,
              },
              1368: {
                slidesPerView: 2,
              }
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
      });

        // Testimonial Carousel
        var Swiper6 = new Swiper('.wptb-testimonial--carousel2 .swiper-container', {
          loop: true,
          // autoplay: {
          //     delay: 4000,
          // },
          speed: 1500,
          slidesPerView: 1,
          // centeredSlides: true,
          spaceBetween: 30,
          breakpoints: {
              320: {
                slidesPerView: 1,
                spaceBetween: 20
              },
              768: {
                slidesPerView: 2,
              },
              1200: {
                slidesPerView: 2,
              },
              1368: {
                slidesPerView: 2,
              }
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
        });

        // Testimonial Carousel
        var Swiper7 = new Swiper('.wptb-testimonial--carousel3 .swiper-container', {
          loop: true,
          speed: 1500,
          slidesPerView: 1,
          spaceBetween: 30,
          breakpoints: {
              320: {
                slidesPerView: 1,
                spaceBetween: 20
              },
              768: {
                slidesPerView: 1,
              },
              1200: {
                slidesPerView: 2,
              },
              1368: {
                slidesPerView: 2,
              }
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
      });

        // Testimonial Carousel
        var SwiperTesti = new Swiper('.wptb-testimonial--carousel4 .swiper-container', {
            loop: true,
            autoplay: {
                delay: 4000,
            },
            speed: 1500,
            slidesPerView: 1,
            spaceBetween: 0,
            breakpoints: {
                320: {
                  slidesPerView: 1,
                },
                768: {
                  slidesPerView: 2,
                },
                1200: {
                  slidesPerView: 2,
                },
                1368: {
                  slidesPerView: 2,
                }
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true
            },
        });

        // Testimonial Carousel
        var Testimonial5 = new Swiper('.wptb-testimonial--carousel5 .swiper-container', {
          loop: true,
          // autoplay: {
          //     delay: 4000,
          // },
          speed: 1500,
          slidesPerView: 1,
          // centeredSlides: true,
          spaceBetween: 70,
          breakpoints: {
              320: {
                slidesPerView: 1,
              },
              768: {
                slidesPerView: 1,
              },
              1200: {
                slidesPerView: 2,
              },
              1368: {
                slidesPerView: 2,
              }
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
        });

        // Team Carousel
        var Swiper8 = new Swiper('.wptb-team-carousel .swiper-container', {
          loop: true,
          // autoplay: {
          //     delay: 4000,
          // },
          speed: 1500,
          slidesPerView: 1,
          // centeredSlides: true,
          spaceBetween: 30,
          breakpoints: {
              320: {
                slidesPerView: 1,
              },
              576: {
                slidesPerView: 2,
              },
              768: {
                slidesPerView: 3,
              },
              1368: {
                slidesPerView: 4,
              }
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
        });

        // Service Carousel
        var Swiper9 = new Swiper('.wptb-case-grid-carousel .swiper-container', {
          loop: true,
          autoplay: {
              delay: 4000,
          },
          speed: 1500,
          slidesPerView: 1,
          spaceBetween: 0,
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          breakpoints: {
              320: {
                slidesPerView: 1,
                spaceBetween: 20
              },
              768: {
                slidesPerView: 2,
                spaceBetween: 20
              },
              1200: {
                slidesPerView: 2,
                spaceBetween: 20,
              },
              1368: {
                slidesPerView: 3,
                spaceBetween: 20,
              }
          },
        });

        // Blog Carousel
        var Swiper10 = new Swiper('.wptb-blog-carousel .swiper-container', {
          loop: true,
          // autoplay: {
          //     delay: 4000,
          // },
          speed: 1500,
          slidesPerView: 1,
          spaceBetween: 30,
          breakpoints: {
              320: {
                slidesPerView: 1,
              },
              768: {
                slidesPerView: 2,
              },
              1200: {
                slidesPerView: 2,
              },
              1368: {
                slidesPerView: 3,
              }
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
        });

         // Blog Carousel
         var Swiper11 = new Swiper('.wptb-blog-carousel2 .swiper-container', {
          loop: true,
          speed: 1500,
          slidesPerView: 1,
          spaceBetween: 30,
          breakpoints: {
              320: {
                slidesPerView: 1,
              },
              768: {
                slidesPerView: 2,
              },
              1200: {
                slidesPerView: 2,
              },
              1368: {
                slidesPerView: 3,
              }
          },
          navigation: {
              nextEl: '.swiper-button-next',
              prevEl: '.swiper-button-prev',
          },
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
        });

        // Service Carousel
        var Swiper12 = new Swiper('.wptb-apps-carousel .swiper-container', {
          loop: true,
          autoplay: {
              delay: 4000,
          },
          speed: 1500,
          slidesPerView: 1,
          centeredSlides: true,
          spaceBetween: 10,
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
          breakpoints: {
              320: {
                slidesPerView: 1,
              },
              768: {
                slidesPerView: 4,
              },
              1200: {
                slidesPerView: 5,
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
              },
              1368: {
                slidesPerView: 5,
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
              }
          },
        });

        // Service Carousel
        var Swiper13 = new Swiper('.wptb-shop-carousel .swiper-container', {
          loop: true,
          autoplay: {
              delay: 4000,
          },
          speed: 1500,
          slidesPerView: 1,
          centeredSlides: true,
          spaceBetween: 20,
          pagination: {
              el: '.swiper-pagination',
              clickable: true
          },
          breakpoints: {
              320: {
                slidesPerView: 1,
              },
              768: {
                slidesPerView: 2,
              },
              1200: {
                slidesPerView: 3,
              },
              1368: {
                slidesPerView: 4,
              }
          },
        });


        // Odometer
        $('.odometer').appear();
        $('.odometer').appear(function(){
          var odo = $(".odometer");
          odo.each(function() {
            var countNumber = $(this).attr("data-count");
            $(this).html(countNumber);
          });
          window.odometerOptions = {
            format: 'd',
          };
        });


        // accordion
        $(".wptb-accordion").on("click",".wptb-item-accordion", function () {
          $(this).next().slideDown();
          $(".wptb-item--content").not($(this).next()).slideUp();
        });

        $(".wptb-accordion").on("click",".wptb--item", function () {
          $(this).addClass("active").siblings().removeClass("active");
        });

        // Split Text Effect
        // splt({
        //     reveal: true
        // });

        // anime({
        //     targets: '.reveal',
        //     translateY: [0, 20],
        //     direction: 'alternate',
        //     loop: 1,
        //     delay: anime.stagger(25),
        //     easing: 'cubicBezier(.71,-0.77,.43,1.67)'
        // });

        new WOW().init();

        function radial_animate() { 
          $('svg.radial-progress').each(function( index, value ) { 

              $(this).find($('circle.bar--animated')).removeAttr( 'style' );    
              // Get element in Veiw port
              var elementTop = $(this).offset().top;
              var elementBottom = elementTop + $(this).outerHeight();
              var viewportTop = $(window).scrollTop();
              var viewportBottom = viewportTop + $(window).height();
              
              if(elementBottom > viewportTop && elementTop < viewportBottom) {
                  var percent = $(value).data('countervalue');
                  var radius = $(this).find($('circle.bar--animated')).attr('r');
                  var circumference = 2 * Math.PI * radius;
                  var strokeDashOffset = circumference - ((percent * circumference) / 100);
                  $(this).find($('circle.bar--animated')).animate({'stroke-dashoffset': strokeDashOffset}, 2800);
              }
          });
      }
        // To check If it is in Viewport 
        var $window = $(window);
        function check_if_in_view() {    
            $('.countervalue').each(function(){
                if ($(this).hasClass('start')){
                    var elementTop = $(this).offset().top;
                    var elementBottom = elementTop + $(this).outerHeight();

                    var viewportTop = $(window).scrollTop();
                    var viewportBottom = viewportTop + $(window).height();

                    if (elementBottom > viewportTop && elementTop < viewportBottom) {
                                $(this).removeClass('start');
                                $('.countervalue').text();
                                var myNumbers = $(this).text();
                                if (myNumbers == Math.floor(myNumbers)) {
                                    $(this).animate({
                                        Counter: $(this).text()
                                    }, {
                                        duration: 2800,
                                        easing: 'swing',
                                        step: function(now) {
                                            $(this).text(Math.ceil(now)  + '%');                                
                                        }
                                    });
                                } else {
                                    $(this).animate({
                                        Counter: $(this).text()
                                    }, {
                                        duration: 2800,
                                        easing: 'swing',
                                        step: function(now) {                                
                                            $(this).text(now.toFixed(2)  + '$'); 
                                        }
                                    });
                                }

                                radial_animate();
                            }
                }
            });
        }
        $window.on('scroll', check_if_in_view);

        

    });      
})(jQuery);

// Hide header on scroll down
const nav = document.querySelector(".header");
const scrollUp = "top-up";
let lastScroll = 800;

window.addEventListener("scroll", () => {
    const currentScroll = window.pageYOffset;
    if (currentScroll <= 800) {
        nav.classList.remove(scrollUp);
        $('.totop').removeClass('show');
        return;
    }
    
    if (currentScroll > lastScroll) {
        // down
        nav.classList.add(scrollUp);
        $('.totop').addClass('show');

    } else if (currentScroll < lastScroll) {
        // up
        nav.classList.remove(scrollUp);
        $('.totop').removeClass('show');
    }
    lastScroll = currentScroll;
});

var typed = new Typed('.typed', {
  strings: ['Studio', 'Agency'],
  typeSpeed: 200,
  loop: true,
  startDelay: 50,
  backSpeed: 100,
});