module Jekyll
  class CollectionIndexGenerator < Generator
    safe true
    priority :high

    def generate(site)
      # Tạo trang collections index
      create_collections_index(site)
      
      # Tạo redirect cho /c/ -> /collections/
      create_c_redirect(site)
      
      # Tạo collections data file
      create_collections_data(site)
    end

    private

    def create_collections_index(site)
      collections_data = get_collections_data(site)
      
      # Tạo trang collections/index.html
      collections_dir = File.join(site.source, 'collections')
      FileUtils.mkdir_p(collections_dir) unless Dir.exist?(collections_dir)
      
      index_page = PageWithoutAFile.new(site, site.source, 'collections', 'index.html')
      index_page.data['layout'] = 'collection-index'
      index_page.data['title'] = 'All Collections'
      index_page.data['description'] = 'Browse all StoryMap collections'
      index_page.data['collections_data'] = collections_data
      index_page.data['permalink'] = '/collections/'
      
      site.pages << index_page
    end

    def create_c_redirect(site)
      # Tạo c/index.html với redirect
      c_dir = File.join(site.source, 'c')
      FileUtils.mkdir_p(c_dir) unless Dir.exist?(c_dir)
      
      redirect_page = PageWithoutAFile.new(site, site.source, 'c', 'index.html')
      redirect_page.data['layout'] = 'redirect'
      redirect_page.data['redirect_to'] = '/collections/'
      redirect_page.data['permalink'] = '/c/'
      
      site.pages << redirect_page
    end

    def create_collections_data(site)
      # Tạo data file cho collections
      collections_data = get_collections_data(site)
      
      data_page = PageWithoutAFile.new(site, site.source, '_data', 'collections.json')
      data_page.content = collections_data.to_json
      data_page.data['layout'] = nil
      
      site.pages << data_page
    end

    def get_collections_data(site)
      collections_data = []
      
      # Lấy tất cả collection files từ _collections
      if site.collections['collections'] && site.collections['collections'].docs
        site.collections['collections'].docs.each do |doc|
          next unless doc.data['layout'] == 'collection'
          
          collections_data << {
            'title' => doc.data['title'],
            'description' => doc.data['description'],
            'category' => doc.data['category'],
            'featured_image' => doc.data['featured_image'],
            'icon' => doc.data['icon'],
            'url' => doc.url,
            'slug' => doc.data['slug'] || File.basename(doc.basename, '.*'),
            'storymaps_count' => doc.data['storymaps']&.size || 0,
            'featured_count' => doc.data['storymaps']&.count { |s| s['featured'] } || 0,
            'date' => doc.date || Time.now
          }
        end
      end
      
      # Sắp xếp theo date giảm dần
      collections_data.sort_by! { |c| c['date'] }.reverse!
      collections_data
    end
  end

  class PageWithoutAFile < Page
    def initialize(site, base, dir, name)
      @site = site
      @base = base
      @dir = dir
      @name = name

      self.process(name)
      self.data = {}
    end

    def read_yaml(*)
      # Override to prevent reading from file
    end
  end
end
