function previewEstimatePDF() {
  const printContents = document.getElementById("estimatePrintable").innerHTML;
  const printWindow = window.open('', '_blank', 'width=900,height=700');
  printWindow.document.write(`
    <html>
      <head>
        <title>Estimate Preview</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { padding: 10px; border: 1px solid #ddd; }
          th { background: #3498db; color: #fff; }
          .total { margin-top: 20px; font-weight: bold; color: #e67e22; text-align: right; }
          .notes { margin-top: 30px; font-style: italic; padding: 12px; background: #f3f3f3; border-left: 4px solid #3498db; }
        </style>
      </head>
      <body>${printContents}</body>
    </html>
  `);
  printWindow.document.close();
  printWindow.focus();
  printWindow.print();
}

function downloadEstimatePDF() {
  const element = document.getElementById("estimatePrintable");
  const opt = {
    margin:       0.5,
    filename:     'estimate.pdf',
    image:        { type: 'jpeg', quality: 0.98 },
    html2canvas:  { scale: 2 },
    jsPDF:        { unit: 'in', format: 'a4', orientation: 'portrait' }
  };
  html2pdf().from(element).set(opt).save();
}
