var scheming_multiple_text_init_done = false;

this.ckan.module('alias-multiple-input', function ($, _) {
    MultipleText = {
        initialize: function () {
            $.proxyAll(this, /_on/);

            this.fieldset = this.el;

            if (!scheming_multiple_text_init_done) {
                $(document).on('click', '.btn-add-alias-input', this._onAddInput)

                $(document).on('click', 'a[name="multiple-remove"]', function (e) {
                    var list = $(this).closest('ol').find('li');

                    if (list.length != 1) {
                        var $curr = $(this).closest('.multiple-text-field');
                        $curr.hide(100, function () {
                            $curr.remove();
                        });
                        e.preventDefault();
                    }
                    else {
                        list.first().find('input').val('');
                    }
                });
                scheming_multiple_text_init_done = true;
            }

            $(this.el).find(".multiple-text-field input").slug();
        },

        _onAddInput: function () {
            let list = this.fieldset.find('ol')
            let items = list.find('li')
            var copy = items.last().clone();
            let input = copy.find('input');
            input.val('');
            list.append(copy);
            input.focus();
            input.slug();
        },
    };
    return MultipleText;
});
