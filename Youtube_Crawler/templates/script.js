 // 獲取下拉式選單元素
  //var url = document.getElementById('inputurl').value
  //console.log(url)
  var videos;
  var selectElement = document.getElementById('highlightChooser');
   fetch('/youtube_chatgpt/data').then(response => response.json())
			.then(data => {
				// 解析 JSON 並存入 JavaScript 陣列
				var videos = data;
				videos.forEach(function(value) {
					console.log(value)
					var option = document.createElement('option');
					option.value = value[2];
					option.textContent = value[2] + 's';
					selectElement.appendChild(option);
					});
					
				//console.log(videos[0][1])
				// 1. This code loads the IFrame Player API code asynchronously.
				var tag = document.createElement('script');
				tag.src = "https://www.youtube.com/iframe_api";
				var firstScriptTag = document.getElementsByTagName('script')[0];
				firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

				selectElement.addEventListener('change', function(event) {
					var selectedOption = event.target.value;
					videoContainer.innerHTML = '';
					var iframe = document.createElement('iframe');
						
					// 設定影片的 src 屬性，並指定影片 ID 和起始時間
					iframe.src = 'https://www.youtube.com/embed/' + videos[0][1]  + '?start=' + selectedOption;

					// 設定其他的屬性和樣式，如高度、寬度等
					iframe.width = '640';
					iframe.height = '390';
					iframe.frameBorder = '0';
						
					// 將 <iframe> 元素插入到容器中
					document.getElementById('videoContainer').appendChild(iframe);
				});
					// 2. This function creates an <iframe> (and YouTube player)
					//    after the API code downloads.
					// 在控制台輸出陣列值
					console.log(videos);
				});