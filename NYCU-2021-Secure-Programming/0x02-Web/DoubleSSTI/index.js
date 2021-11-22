var handlebars = require('handlebars');

var scope = {
  name: "input",
  secret: "secret",
  // people: {
  //   data: ["hank", "tommy", "calehan"],
  //   hi_there: name => `Hi! There u are, ${name}!`
  // },
}

tstr = `
{{#each this}}
  Key: {{@key}} -> {{this}}
{{/each}}
`

var template = handlebars.compile(tstr);
var html = template(scope);
console.log(html)