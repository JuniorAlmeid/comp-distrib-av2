require 'sinatra'
require 'open-uri'
require 'nokogiri'
require 'json'

set :bind, '0.0.0.0'
set :port, 5000

get '/api/*?' do
  url = [params['splat'].first, request.query_string].reject(&:empty?).join("?")
  
  begin
    doc = Nokogiri::HTML(URI.open(url, "User-Agent" => "Mozilla/5.0", :read_timeout => 10))
    links = doc.css('a').map { |a| a['href'] }.compact
    
    status 200
    headers "content-type" => "application/json"
    body({ url: url, links: links }.to_json)
  rescue => e
    status 400
    { error: e.message }.to_json
  end
end