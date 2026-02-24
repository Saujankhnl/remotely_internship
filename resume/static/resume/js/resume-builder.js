document.addEventListener('DOMContentLoaded', function() {
    const radios = document.querySelectorAll('input[name="template"]');
    const previewFrame = document.getElementById('previewFrame');
    const downloadTemplate = document.getElementById('downloadTemplate');
    const templateLabel = document.getElementById('templateLabel');
    const previewBtn = document.getElementById('previewBtn');

    const previewUrlTemplate = previewFrame.dataset.previewUrl;

    const labelMap = {
        'professional': 'Professional Template',
        'modern': 'Modern Template',
        'minimal': 'Minimal Template'
    };

    function getSelected() {
        const checked = document.querySelector('input[name="template"]:checked');
        return checked ? checked.value : 'professional';
    }

    function updatePreview() {
        const template = getSelected();
        downloadTemplate.value = template;
        templateLabel.textContent = labelMap[template] || template;
        previewFrame.src = previewUrlTemplate.replace('PLACEHOLDER', template);
    }

    radios.forEach(radio => {
        radio.addEventListener('change', updatePreview);
    });

    previewBtn.addEventListener('click', updatePreview);
});
