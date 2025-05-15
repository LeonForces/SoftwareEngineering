math.randomseed(os.time())

wrk.method = "GET"
wrk.headers["Content-Type"] = "application/json"

request = function()
    local user_id = math.random(1, 10000)
    local path = "/dev/users/cache/" .. user_id
    -- local path = "/dev/users/" .. user_id
    return wrk.format(nil, path)
end