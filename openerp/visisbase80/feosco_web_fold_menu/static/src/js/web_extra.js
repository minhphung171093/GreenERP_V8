/**
 * Created by thanhchatvn@gmail.com
 */
openerp.feosco_web_fold_menu = function (instance) {
    instance.web.WebClient = instance.web.WebClient.extend({
        events: {
            'click .oe_toggle_secondary_menu': 'fold_menu'
        },
        fold_menu: function () {
            $('span.oe_menu_fold').toggle()
            $('span.oe_menu_unfold').toggle()
            $('.oe_logo').toggleClass("hidden_element")
            $('.oe_secondary_menus_container').toggleClass("hidden_element")
            $('.oe_leftbar').toggleClass("oe_leftbar_folded")
			$('.oe_footer').toggle()

        }
    })
}