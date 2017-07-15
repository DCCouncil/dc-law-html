$(document).ready(function() {
  function renderMustacheData(data) {
    $('title, body').each(function(_, el) {
      var template = $(el).html();
      var rendered = Mustache.render(template, data);
      $(el).html(rendered);
    });
  }

  function triggerGitHubCalls() {
    $('[data-repo]').each(function(_, el) {
      var repo = $(el).data('repo');
      var branch = $(el).data('branch') || 'master';

      $.get('https://api.github.com/repos/' + repo + '/commits/' + branch, function(data) {
        var headSha = data.sha;
        var thisSha = $(el).text();

        if (headSha === thisSha) {
          $(el).addClass('success');
        } else {
          $(el).addClass('error');
          var tooltip = [
            'Latest: ' + headSha,
            'Date: ' + data.commit.committer.date,
            'Message: ' + data.commit.message
          ].join('\n')
          $(el).prop('title', tooltip);
        }
      }, 'json');
    });
  }

  $.get($('body').data('url'), renderMustacheData, 'json').then(triggerGitHubCalls);
});
