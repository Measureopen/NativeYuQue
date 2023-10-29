jQuery(document).ready(function(){
  function renderSelectOptions(data) {
    var select = $('#repotSelect');
    // 清空现有的选项
    select.empty();
    // 遍历JSON数据并添加选项
    for (var i = 0; i < data.length; i++) {
        var option = $('<option>').attr('value', data[i].name).text(data[i].name);
        select.append(option);
    }

    // 刷新下拉选择框（如果使用了特定的选择框插件）
    select.selectpicker('refresh');
};
  function doStep(){
    // Next Button
    $('a.next-step').click(function(event){
          // 获取文本框中的值
    var spaceName = $('#spaceName').val();
    var tokenValue = $('#tokenValue').val();

    // 创建一个包含数据的对象
    var data = {
        spaceName: spaceName,
        tokenValue: tokenValue
    };
    // 发送ajax请求-获取个人知识库
      $.ajax({
                url: "/getRepo/",
                type: "POST",
                data: data,
                dataType: "JSON",
                success: function (res) {
                    if (res.status) {
                      // 下拉框渲染数据
                       renderSelectOptions(res.data);
                    } else {

                    }
                }
            });
      event.preventDefault();
      // Part 1
      if($('.alpha').hasClass("in")) {
        $('.alpha').removeClass("in");
      }
      $('.alpha').addClass("out");
      // Part 2
      if($('.beta').hasClass("out")) {
        $('.beta').removeClass("out");
      }
      $('.beta').addClass("in");
    });

    // Previous Button
    $('a.prev-step').click(function(event){
      event.preventDefault();
      $('.alpha').removeClass("out").addClass("in");
      $('.beta').removeClass("in").addClass("out");
    });

    // Submit & Complete
    $('.submit').click(function(event){
      var selectedValues = $('#repotSelect').val();
      var selectedData = {
        "selected": selectedValues,
      }
      // 发送Ajax数据-开始下载知识库
      $.ajax({
                url: "/downloadRepo/",
                type: "POST",
                data: selectedData,
                dataType: "JSON",
                success: function (res) {
                    if (res.status) {
                        // 修改HTML内容
                    $("#status").text("下载完成,3s后自动跳转到知识库页面");

                    // 执行页面跳转
                    setTimeout(function() {
                        window.location.href = "/index/"; // 用你想跳转的页面替换此处
                    }, 3000); //
                    } else {

                    }
                }
            })
      event.preventDefault();
      // Part 1
      if($('.beta').hasClass("in")) {
        $('.beta').removeClass("in");
      }
      $('.beta').addClass("out");
      // Part 2
      if($('.charlie').hasClass("out")) {
        $('.charlie').removeClass("out");
      }
      $('.charlie').addClass("in");
    });
  }
  // Active Functions
  doStep();
});
