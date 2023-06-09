fetch('http://localhost:8000/zuu/')
  .then(response => response.json())
  .then(data => {
    const jsonString = data.response;
    console.log(jsonString);
    const jsonObject = JSON.parse(jsonString);
    console.log(jsonObject.hariu);    
    console.log(jsonObject.surguuli); 
  })
  .catch(error => {
    console.error('Error:', error);
  });
