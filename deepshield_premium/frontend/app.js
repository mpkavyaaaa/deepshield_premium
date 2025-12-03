const BACKEND = 'https://deepshield-premium.onrender.com';
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const resultCard = document.getElementById('result');
const resultContent = document.getElementById('result-content');
const previewImg = document.getElementById('preview-img');
const previewVideo = document.getElementById('preview-video');
const preview = document.getElementById('preview');

function showResult(obj){
  resultCard.classList.remove('hidden');
  const html = `
    <p><strong>Prediction:</strong> ${obj.prediction}</p>
    <p><strong>Score:</strong> ${ (obj.score*100).toFixed(2) }% (probability-of-real)</p>
    ${obj.frames_sampled ? '<p><strong>Frames sampled:</strong> ' + obj.frames_sampled + '</p>' : ''}
    <pre style="background:#061224;padding:8px;border-radius:8px;margin-top:8px">${JSON.stringify(obj,null,2)}</pre>
  `;
  resultContent.innerHTML = html;
}

fileInput.addEventListener('change', (e)=>{
  const file = e.target.files[0];
  if(!file) return;
  if(file.type.startsWith('image/')){
    previewVideo.classList.add('hidden');
    previewImg.src = URL.createObjectURL(file);
    previewImg.classList.remove('hidden');
  } else if(file.type.startsWith('video/')){
    previewImg.classList.add('hidden');
    previewVideo.src = URL.createObjectURL(file);
    previewVideo.classList.remove('hidden');
  } else {
    previewImg.classList.add('hidden');
    previewVideo.classList.add('hidden');
  }
});

uploadBtn.addEventListener('click', async ()=>{
  const file = fileInput.files[0];
  if(!file){ alert('Please select an image or video file'); return; }
  uploadBtn.disabled = true;
  uploadBtn.innerText = 'Analyzing...';
  resultCard.classList.add('hidden');
  try{
    const form = new FormData();
    form.append('file', file, file.name);
    let res;
    if(file.type.startsWith('image/')){
      res = await fetch(BACKEND + '/predict-image', { method:'POST', body: form });
    } else {
      // video
      // optional: send sample_rate to downsample frames
      form.append('sample_rate', 5);
      res = await fetch(BACKEND + '/predict-video', { method:'POST', body: form });
    }
    if(!res.ok){
      const txt = await res.text();
      alert('Server error: ' + txt);
    } else {
      const data = await res.json();
      showResult(data);
    }
  }catch(err){
    alert('Request failed: ' + err);
  }finally{
    uploadBtn.disabled = false;
    uploadBtn.innerText = 'Upload & Analyze';
  }
});
