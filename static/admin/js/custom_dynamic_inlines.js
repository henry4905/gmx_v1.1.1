(function($) {
    $(document).ready(function() {
        function updateTotalForms(prefix) {
            var totalForms = $('#id_' + prefix + '-TOTAL_FORMS');
            var forms = $('.dynamic-' + prefix);
            totalForms.val(forms.length);
        }

        $('.add-row a').click(function(e) {
            e.preventDefault();
            var inlineGroup = $(this).closest('.inline-group');
            var prefix = inlineGroup.attr('id').replace('-group', '');
            var totalForms = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
            var emptyForm = $('#' + prefix + '-empty').clone(true);
            var newFormHtml = emptyForm.html().replace(/__prefix__/g, totalForms);
            emptyForm.remove();
            inlineGroup.find('.inline-related:last').after('<div class="inline-related dynamic-' + prefix + '">' + newFormHtml + '</div>');
            $('#id_' + prefix + '-TOTAL_FORMS').val(totalForms + 1);
        });

        $(document).on('click', '.inline-deletelink', function(e) {
            e.preventDefault();
            var inline = $(this).closest('.inline-related');
            var inlineGroup = $(this).closest('.inline-group');
            var prefix = inlineGroup.attr('id').replace('-group', '');
            inline.remove();
            updateTotalForms(prefix);
            $('.dynamic-' + prefix).each(function(index) {
                $(this).find(':input').each(function() {
                    var name = $(this).attr('name');
                    var id = $(this).attr('id');
                    if (name) $(this).attr('name', name.replace(/\-\d+\-/, '-' + index + '-'));
                    if (id) $(this).attr('id', id.replace(/\-\d+\-/, '-' + index + '-'));
                });
            });
        });
    });
})(django.jQuery);