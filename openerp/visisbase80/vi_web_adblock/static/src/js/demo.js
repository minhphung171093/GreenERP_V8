openerp.vi_web_adblock = function (instance) {


//    console.log('remove pop-up');

    instance.web.WebClient.include({
        show_application: function() {
//            alert('');
            this._super.apply(this, arguments);
        },
        _ab_location: function(dbuuid) {
//            alert('mine');
            this._super.apply(this, arguments);
        },
        show_annoucement_bar: function() {
//            alert('mine');
            this._super.apply(this, arguments);
        }


    });





}