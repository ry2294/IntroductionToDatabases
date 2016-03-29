var app = angular.module('stackoverflowApp', ['ui.router']);

app.config(function($stateProvider, $urlRouterProvider) {
  $urlRouterProvider.otherwise('/login');
  
  $stateProvider.state('login', {
    templateUrl: 'login.html',
    url: '/login',
    controller: 'loginController'
  })
  .state('search', {
      templateUrl: 'search.html',
      url: '/search',
      controller: 'searchController'
  })
  .state('createQuestion', {
      templateUrl: 'createQuestion.html',
      url: '/createQuestion',
      controller: 'createQuestionController'
  })
  .state('admin', {
      templateUrl: 'admin.html',
      url: '/admin',
      controller: 'adminController'
  })
  .state('question', {
    templateUrl: 'question.html',
    url: '/search',
    controller: 'questionController'
  });
});

app.controller('navigationController', function($scope, $state, $rootScope) {
    console.log("Testing Navigation");
    
    $scope.logout = function() {$state.go('login');};
    $scope.isLoggedIn = function() {return !$state.is('login')};
    $rootScope.user = {userid: "5969614"};
});

app.controller('loginController', function($scope, $state) {
    $scope.authenticate = function() {
        /* 
            OAuth Stuff
        */
        
        $state.go('search');
    };
});

app.controller('questionController', function($scope, $rootScope, $state, $http) {
    $scope.question = $rootScope.selectedQuestion;
    $scope.back = function() {$state.go('search')};
    
    $http({
        method: 'POST',
        url: '/question',
        data: {query: $scope.question.questionid},
        transformResponse: function (data, headersGetter, status) {
            return {data: data};
        }
    }).success(function (response, status) {
        var answermap = JSON.parse(response.data);
        var answers = [];
        for (var key in answermap) {
            answers.push(answermap[key]);
        }
        $scope.question.answers = answers;
    }).error(function () {
        console.log('failure');
    });
    
    $scope.createAnswer = function() {
        if($scope.newanswer == null) return alert('Please enter answer');
        $http({
            method: 'POST',
            url: '/insertanswer',
            data: {
                userid: $rootScope.user.userid,
                questionid: $scope.question.questionid,
                body: $scope.newanswer
            },
            transformResponse: function (data, headersGetter, status) {
                return {data: data};
            }
        }).success(function (response, status) {
            console.log(status);
            $state.reload('question');
        }).error(function () {
            console.log('failure');
        });
    };
    
    $scope.createComment = function(answerid) {
        var textId = "#" + answerid;
        console.log(answerid + ' text = ' + $(textId).val());
        $http({
            method: 'POST',
            url: '/insertcomment',
            data: {
                userid: $rootScope.user.userid,
                answerid: answerid,
                body: $(textId).val()
            },
            transformResponse: function (data, headersGetter, status) {
                return {data: data};
            }
        }).success(function (response, status) {
            console.log(status);
            $state.reload('question');
        }).error(function () {
        });
    };
});

app.controller('searchController', function($scope, $rootScope, $state, $http) {
    console.log('Testing Search');
    $scope.questions = {};
    
    $scope.viewQuestion = function(index) {
        $rootScope.selectedQuestion = $scope.questions[index];
        console.log($rootScope.selectedQuestion.questionid);
        $state.go('question');
    };
    
    $scope.searchQuery = function() {
        
        if($scope.query == null || $scope.query == "") alert('test');
        else {
            $http({
                method: 'POST',
                url: '/search',
                data: {query: $scope.query},
                transformResponse: function (data, headersGetter, status) {
                    return {data: data};
                }
            }).success(function (response, status) {
                $scope.questions = JSON.parse(response.data);
            }).error(function () {
                console.log('failure');
            });
        }
    }
});

app.controller('createQuestionController', function($scope, $http, $rootScope) {
    $scope.question = {};
    $scope.error = "";
    
    $http({
        method: 'POST',
        url: '/tags',
        data: {},
        transformResponse: function (data, headersGetter, status) {
            return {data: data};
        }
    }).success(function (response, status) {
        $scope.allTags = JSON.parse(response.data);
    }).error(function () {
        console.log('failure');
    });
    
    $scope.createQuestion = function() {
        if($scope.question.title == null) $scope.error = "Enter a title for the question";
        else if($scope.question.body == null) $scope.error = "Enter description for the question";
        else if($scope.selectedTags == null || $scope.selectedTags.length <= 0) $scope.error = "Please select atleast one Tag";
        else {
            $http({
                method: 'POST',
                url: '/insertquestion',
                data: {
                    userid: $rootScope.user.userid,
                    title: $scope.question.title,
                    body: $scope.question.body,
                    tags: $scope.selectedTags
                },
                transformResponse: function (data, headersGetter, status) {
                    return {data: data};
                }
            }).success(function (response, status) {
                $scope.error="Question Created Successfully";
                $scope.question.title = null; $scope.question.body = null; $scope.selectedTags = null; 
            }).error(function () {
                $scope.error = 'Server error while creating question';
            });
        }
    };
    console.log('Testing Create Question');
});

app.controller('adminController', function($scope, $http) {
    console.log('Testing admin Page');
    $scope.user = {};
    $scope.fecthUser = function() {
        $http({
            method: 'POST',
            url: '/userinfo',
            data: {username: $scope.username},
            transformResponse: function (data, headersGetter, status) {
                return {data: data};
            }
        }).success(function (response, status) {
            $scope.user = JSON.parse(response.data) != null ? JSON.parse(response.data)[0] : {};
            console.log($scope.user);
        }).error(function () {
            console.log('failure');
        });
    }
    $scope.assignableBadges = ["Bronze"];
    $scope.removableBadges = ["Silver", "Gold"];
});